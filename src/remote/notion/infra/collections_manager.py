"""The handler of collections on Notion side."""
import logging
from dataclasses import field, dataclass
from pathlib import Path
from types import TracebackType
from typing import Callable, TypeVar, Final, Dict, Optional, Iterable, cast, ClassVar

import typing

from notion.collection import CollectionRowBlock

from models.basic import EntityId
from remote.notion.infra.client import NotionClient
from remote.notion.common import NotionId, NotionPageLink, NotionCollectionLink, NotionLockKey, \
    NotionCollectionLinkExtra
from remote.notion.infra.connection import NotionConnection
from utils.storage import JSONDictType, BaseRecordRow, RecordsStorage, Eq
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class BaseItem:
    """A basic item type, which must contain a Notion id and an local id."""

    notion_id: NotionId
    ref_id: Optional[str]


ItemType = TypeVar("ItemType", bound=BaseItem)
CopyRowToNotionRowType = Callable[[NotionClient, ItemType, CollectionRowBlock], CollectionRowBlock]
CopyNotionRowToRowType = Callable[[CollectionRowBlock], ItemType]


@dataclass()
class _CollectionLockRow(BaseRecordRow):
    """Information about a Notion-side collection."""
    page_id: NotionId
    collection_id: NotionId
    view_ids: Dict[str, NotionId] = field(default_factory=dict, compare=False)


@dataclass()
class _CollectionItemLockRow(BaseRecordRow):
    """Information about a Notion-side collection item."""
    collection_key: NotionLockKey
    ref_id: EntityId
    row_id: NotionId


class CollectionsManager:
    """The handler for collections on Notion side."""

    _COLLECTIONS_STORAGE_PATH: ClassVar[Path] = Path("/data/notion.collections.yaml")
    _COLLECTION_ITEMS_STORAGE_PATH: ClassVar[Path] = Path("/data/notion.collection-items.yaml")

    _connection: Final[NotionConnection]
    _collections_storage: Final[RecordsStorage[_CollectionLockRow]]
    _collection_items_storage: Final[RecordsStorage[_CollectionItemLockRow]]

    def __init__(self, time_provider: TimeProvider, connection: NotionConnection) -> None:
        """Constructor."""
        self._connection = connection
        self._collections_storage = \
            RecordsStorage[_CollectionLockRow](
                self._COLLECTIONS_STORAGE_PATH, time_provider, CollectionsManager._CollectionsStorageProtocol())
        self._collection_items_storage = \
            RecordsStorage[_CollectionItemLockRow](
                self._COLLECTION_ITEMS_STORAGE_PATH, time_provider,
                CollectionsManager._CollectionItemsStorageProtocol())

    def __enter__(self) -> 'CollectionsManager':
        """Enter context."""
        self._collections_storage.initialize()
        self._collection_items_storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def upsert_collection(
            self, key: NotionLockKey, parent_page: NotionPageLink, name: str, schema: JSONDictType,
            view_schemas: Dict[str, JSONDictType]) -> NotionCollectionLink:
        """Create the Notion-side structure for this collection."""
        lock = self._collections_storage.load_optional(key)

        client = self._connection.get_notion_client()

        if lock:
            page = client.get_collection_page_by_id(lock.page_id)
            LOGGER.info(f"Found the already existing page as {page.id}")
            collection = client.get_collection(lock.page_id, lock.collection_id, lock.view_ids.values())
            LOGGER.info(f"Found the already existing collection {collection.id}")
        else:
            page = client.create_collection_page(parent_page=client.get_regular_page(parent_page.page_id))
            LOGGER.info(f"Created the page as {page.id}")
            collection = client.create_collection(page, schema)
            LOGGER.info(f"Created the collection as {collection}")

        # Change the schema.

        old_schema = collection.get("schema")
        final_schema = self._merge_notion_schemas(old_schema, schema)
        collection.set("schema", final_schema)
        LOGGER.info("Applied the most current schema to the collection")

        # Attach the views.
        view_ids = lock.view_ids if lock else {}
        for view_name, view_schema in view_schemas.items():
            the_view = client.attach_view_to_collection_page(
                page, collection, view_ids.get(view_name, None), cast(str, view_schema["type"]), view_schema)
            view_ids[view_name] = the_view.id
            LOGGER.info(f"Attached view '{view_name}' to collection id='{collection.id}'")

        # Tie everything up.

        page.set("collection_id", collection.id)
        page.set("view_ids", list(view_ids.values()))

        # Change the title.

        page.title = name
        collection.name = name
        LOGGER.info("Changed the name")

        # Save local locks.
        new_lock = _CollectionLockRow(
            key=key,
            page_id=page.id,
            collection_id=collection.id,
            view_ids=view_ids)

        if lock:
            self._collections_storage.update(new_lock)
        else:
            self._collections_storage.create(new_lock)
        LOGGER.info("Saved lock structure")

        return NotionCollectionLink(page_id=page.id, collection_id=collection.id)

    def remove_collection(self, key: NotionLockKey) -> None:
        """Remove the Notion-side structure for this collection."""
        lock = self._collections_storage.load(key)
        client = self._connection.get_notion_client()

        page = client.get_collection_page_by_id(lock.page_id)
        page.remove()

        self._collections_storage.remove(key)

    def get_collection(self, key: NotionLockKey) -> NotionCollectionLinkExtra:
        """Retrive the Notion-side structure for this collection."""
        lock = self._collections_storage.load(key)
        client = self._connection.get_notion_client()
        page = client.get_collection_page_by_id(lock.page_id)
        return NotionCollectionLinkExtra(
            page_id=lock.page_id,
            collection_id=lock.collection_id,
            name=page.title)

    def update_collection(self, key: NotionLockKey, new_name: str, new_schema: JSONDictType) -> None:
        """Just updates the name and schema for the collection and asks no questions."""
        lock = self._collections_storage.load(key)
        client = self._connection.get_notion_client()
        page = client.get_collection_page_by_id(lock.page_id)
        collection = client.get_collection(lock.page_id, lock.collection_id, lock.view_ids.values())
        page.title = new_name
        collection.name = new_name
        client.update_collection_schema(lock.page_id, lock.collection_id, new_schema)

    @staticmethod
    def _build_item_key(collection_key: str, key: str) -> str:
        return f"{collection_key}:{key}"

    def upsert_collection_item(
            self, collection_key: NotionLockKey, key: NotionLockKey, new_row: ItemType,
            copy_row_to_notion_row: CopyRowToNotionRowType[ItemType]) -> ItemType:
        """Create a Notion entity."""
        if new_row.ref_id is None:
            raise Exception("Can only create over an entity which has a ref_id")

        collection_lock = self._collections_storage.load(collection_key)
        item_key = self._build_item_key(collection_key, key)
        lock = self._collection_items_storage.load_optional(item_key)

        client = self._connection.get_notion_client()
        collection = client.get_collection(
            collection_lock.page_id, collection_lock.collection_id, collection_lock.view_ids.values())

        if lock:
            notion_row = client.get_collection_row(collection, lock.row_id)
            LOGGER.info(f"Entity already exists on Notion side with id={notion_row.id}")
        else:
            notion_row = client.create_collection_row(collection)
            LOGGER.info(f"Created new row on Notion side with id={notion_row.id}")

        new_row.notion_id = notion_row.id

        new_lock = _CollectionItemLockRow(
            key=item_key,
            collection_key=collection_key,
            row_id=notion_row.id,
            ref_id=EntityId(new_row.ref_id))

        if lock:
            self._collection_items_storage.update(new_lock)
        else:
            self._collection_items_storage.create(new_lock)
        LOGGER.info("Saved local locks")

        copy_row_to_notion_row(client, new_row, notion_row)
        LOGGER.info(f"Created new entity with id {notion_row.id}")

        return new_row

    def quick_link_local_and_notion_entries(
            self, key: NotionLockKey, collection_key: NotionLockKey, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        item_key = self._build_item_key(collection_key, key)
        lock = self._collection_items_storage.load_optional(item_key)
        new_lock = _CollectionItemLockRow(
            key=item_key,
            collection_key=collection_key,
            row_id=notion_id,
            ref_id=ref_id)
        if lock is not None:
            LOGGER.warning(f"Entity already exists on Notion side for entity with id={ref_id}")
            self._collection_items_storage.update(new_lock)
        else:
            self._collection_items_storage.create(new_lock)

    def quick_archive(self, key: NotionLockKey, collection_key: NotionLockKey) -> None:
        """Remove a particular entity."""
        item_key = self._build_item_key(collection_key, key)
        collection_lock = self._collections_storage.load(collection_key)
        lock = self._collection_items_storage.load(item_key)
        client = self._connection.get_notion_client()
        collection = client.get_collection(
            collection_lock.page_id, collection_lock.collection_id, collection_lock.view_ids.values())
        notion_row = client.get_collection_row(collection, lock.row_id)
        notion_row.archived = True

    def load_all(
            self, collection_key: NotionLockKey,
            copy_notion_row_to_row: CopyNotionRowToRowType[ItemType]) -> Iterable[ItemType]:
        """Retrieve all the Notion-side entitys."""
        collection_lock = self._collections_storage.load(collection_key)
        client = self._connection.get_notion_client()
        collection = client.get_collection(
            collection_lock.page_id, collection_lock.collection_id, collection_lock.view_ids.values())
        all_notion_rows = client.get_collection_all_rows(collection, collection_lock.view_ids["database_view_id"])

        return [copy_notion_row_to_row(nr) for nr in all_notion_rows]

    def load(
            self, key: NotionLockKey, collection_key: NotionLockKey,
            copy_notion_row_to_row: CopyNotionRowToRowType[ItemType]) -> ItemType:
        """Retrieve the Notion-side entity associated with a particular entity."""
        item_key = self._build_item_key(collection_key, key)
        collection_lock = self._collections_storage.load(collection_key)
        lock = self._collection_items_storage.load(item_key)
        client = self._connection.get_notion_client()
        collection = client.get_collection(collection_lock.page_id, collection_lock.collection_id,
                                           collection_lock.view_ids.values())
        notion_row = client.get_collection_row(collection, lock.row_id)
        return copy_notion_row_to_row(notion_row)

    def save(
            self, key: NotionLockKey, collection_key: NotionLockKey, row: ItemType,
            copy_row_to_notion_row: CopyRowToNotionRowType[ItemType]) -> ItemType:
        """Update the Notion-side entity with new data."""
        if row.ref_id is None:
            raise Exception("Can only save over an entity which has a ref_id")

        item_key = self._build_item_key(collection_key, key)
        collection_lock = self._collections_storage.load(collection_key)
        lock = self._collection_items_storage.load(item_key)
        client = self._connection.get_notion_client()
        collection = client.get_collection(collection_lock.page_id, collection_lock.collection_id,
                                           collection_lock.view_ids.values())
        notion_row = client.get_collection_row(collection, lock.row_id)
        copy_row_to_notion_row(client, row, notion_row)

        return row

    def load_all_saved_notion_ids(self, collection_key: NotionLockKey) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids."""
        return [r.row_id for r
                in self._collection_items_storage.find_all(collection_key=Eq(collection_key))]

    def drop_all(self, collection_key: NotionLockKey) -> None:
        """Hard remove all the Notion-side entities."""
        collection_lock = self._collections_storage.load(collection_key)
        client = self._connection.get_notion_client()
        collection = client.get_collection(
            collection_lock.page_id, collection_lock.collection_id, collection_lock.view_ids.values())

        all_notion_rows = client.get_collection_all_rows(collection, collection_lock.view_ids["database_view_id"])

        for notion_row in all_notion_rows:
            notion_row.remove()

        for item in self._collection_items_storage.find_all(collection_key=Eq(collection_key)):
            item_key = self._build_item_key(collection_key, item.key)
            self._collection_items_storage.remove(item_key)

    def hard_remove(self, key: NotionLockKey, collection_key: NotionLockKey) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        item_key = self._build_item_key(collection_key, key)
        collection_lock = self._collections_storage.load(collection_key)
        lock = self._collection_items_storage.load(item_key)
        client = self._connection.get_notion_client()
        collection = client.get_collection(collection_lock.page_id, collection_lock.collection_id,
                                           collection_lock.view_ids.values())
        notion_row = client.get_collection_row(collection, lock.row_id)
        notion_row.remove()
        self._collection_items_storage.remove(item_key)

    @staticmethod
    @typing.no_type_check
    def _merge_notion_schemas(old_schema: JSONDictType, new_schema: JSONDictType) -> JSONDictType:
        """Merge an old and new schema for the collection."""
        combined_schema = {}

        # Merging schema is limited right now. Basically we assume the new schema takes
        # precedence over the old one, except for select and multi_select, which have a set
        # of options for them which are identified by "id"s. We wanna keep these stable
        # across schema updates.
        # As a special case, the big plan item is left to whatever value it had before
        # since this thing is managed via the big plan syncing flow!
        # As another special case, the recurring tasks group key is left to whatever value it had
        # before since this thing is managed by the other flows!
        for (schema_item_name, schema_item) in new_schema.items():
            if schema_item_name == "bigplan2":
                combined_schema[schema_item_name] = old_schema[schema_item_name] \
                    if (schema_item_name in old_schema and old_schema[schema_item_name]["type"] == "select") \
                    else schema_item
            elif schema_item["type"] == "select" or schema_item["type"] == "multi_select":
                if schema_item_name in old_schema:
                    old_v = old_schema[schema_item_name]

                    combined_schema[schema_item_name] = {
                        "name": schema_item["name"],
                        "type": schema_item["type"],
                        "options": []
                    }

                    for option in schema_item["options"]:
                        old_option = next((old_o for old_o in old_v["options"] if old_o["value"] == option["value"]),
                                          None)
                        if old_option is not None:
                            combined_schema[schema_item_name]["options"].append({
                                "color": option["color"],
                                "value": option["value"],
                                "id": old_option["id"]
                            })
                        else:
                            combined_schema[schema_item_name]["options"].append(option)
                else:
                    combined_schema[schema_item_name] = schema_item
            else:
                combined_schema[schema_item_name] = schema_item

        return combined_schema

    class _CollectionsStorageProtocol:
        @staticmethod
        def storage_schema() -> JSONDictType:
            """The schema for the data."""
            return {
                "page_id": {"type": "string"},
                "collection_id": {"type": "string"},
                "view_ids": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                }
            }

        @staticmethod
        def storage_to_live(storage_form: JSONDictType) -> _CollectionLockRow:
            """Transform the data reconstructed from basic storage into something useful for the live system."""
            return _CollectionLockRow(
                key=NotionLockKey(typing.cast(str, storage_form["key"])),
                page_id=NotionId(typing.cast(str, storage_form["page_id"])),
                collection_id=NotionId(cast(str, storage_form["collection_id"])),
                view_ids={k: NotionId(v) for (k, v) in cast(Dict[str, str], storage_form["view_ids"]).items()})

        @staticmethod
        def live_to_storage(live_form: _CollectionLockRow) -> JSONDictType:
            """Transform the live system data to something suitable for basic storage."""
            return {
                "page_id": live_form.page_id,
                "collection_id": live_form.collection_id,
                "view_ids": live_form.view_ids,
            }

    class _CollectionItemsStorageProtocol:
        @staticmethod
        def storage_schema() -> JSONDictType:
            """The schema for the data."""
            return {
                "key": {"type": "string"},
                "collection_key": {"type": "string"},
                "ref_id": {"type": "string"},
                "row_id": {"type": "string"}
            }

        @staticmethod
        def storage_to_live(storage_form: JSONDictType) -> _CollectionItemLockRow:
            """Transform the data reconstructed from basic storage into something useful for the live system."""
            return _CollectionItemLockRow(
                key=NotionLockKey(typing.cast(str, storage_form["key"])),
                collection_key=NotionLockKey(typing.cast(str, storage_form["collection_key"])),
                ref_id=EntityId(typing.cast(str, storage_form["ref_id"])),
                row_id=NotionId(typing.cast(str, storage_form["row_id"])))

        @staticmethod
        def live_to_storage(live_form: _CollectionItemLockRow) -> JSONDictType:
            """Transform the live system data to something suitable for basic storage."""
            return {
                "collection_key": live_form.collection_key,
                "ref_id": live_form.ref_id,
                "row_id": live_form.row_id
            }

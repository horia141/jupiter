"""The handler of collections on Notion side."""
import dataclasses
import hashlib
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
import typing
from typing import Callable, TypeVar, Final, Dict, Optional, Iterable, cast, ClassVar

from notion.collection import CollectionRowBlock

from framework.json import JSONDictType
from framework.base.entity_id import EntityId
from framework.notion import BaseNotionRow, NotionId
from remote.notion.infra.client import NotionClient, NotionCollectionSchemaProperties
from remote.notion.common import NotionPageLink, NotionCollectionLink, NotionLockKey, \
    NotionCollectionLinkExtra
from remote.notion.infra.connection import NotionConnection
from utils.storage import BaseRecordRow, RecordsStorage, Eq, StructuredStorageError
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


ItemType = TypeVar("ItemType", bound=BaseNotionRow)
CopyRowToNotionRowType = Callable[[NotionClient, ItemType, CollectionRowBlock], CollectionRowBlock]
CopyNotionRowToRowType = Callable[[CollectionRowBlock], ItemType]


@dataclass()
class _NotionCollectionTagLink:
    """Info about a particular tag in a collection."""
    notion_id: NotionId
    collection_id: NotionId
    name: str
    ref_id: Optional[EntityId]

    @property
    def tmp_ref_id_as_str(self) -> Optional[str]:
        """A temporary string value for ref sid."""
        return str(self.ref_id) if self.ref_id else None


@dataclass()
class _CollectionLockRow(BaseRecordRow):
    """Information about a Notion-side collection."""
    page_id: NotionId
    collection_id: NotionId
    view_ids: Dict[str, NotionId] = dataclasses.field(default_factory=dict, compare=False)


@dataclass()
class _CollectionFieldTagLockRow(BaseRecordRow):
    """Information about a Notion-side collection field tag."""
    collection_key: NotionLockKey
    ref_id: EntityId
    field: str
    tag_id: NotionId


@dataclass()
class _CollectionItemLockRow(BaseRecordRow):
    """Information about a Notion-side collection item."""
    collection_key: NotionLockKey
    ref_id: EntityId
    row_id: NotionId


class CollectionsManager:
    """The handler for collections on Notion side."""

    _COLLECTIONS_STORAGE_PATH: ClassVar[Path] = Path("./notion.collections.yaml")
    _COLLECTION_FIELD_TAGS_STORAGE_PATH: ClassVar[Path] = Path("./notion.collection-field-tags.yaml")
    _COLLECTION_ITEMS_STORAGE_PATH: ClassVar[Path] = Path("./notion.collection-items.yaml")

    _connection: Final[NotionConnection]
    _collections_storage: Final[RecordsStorage[_CollectionLockRow]]
    _collection_field_tags_storage: Final[RecordsStorage[_CollectionFieldTagLockRow]]
    _collection_items_storage: Final[RecordsStorage[_CollectionItemLockRow]]

    def __init__(self, time_provider: TimeProvider, connection: NotionConnection) -> None:
        """Constructor."""
        self._connection = connection
        self._collections_storage = \
            RecordsStorage[_CollectionLockRow](
                self._COLLECTIONS_STORAGE_PATH, time_provider, CollectionsManager._CollectionsStorageProtocol())
        self._collection_field_tags_storage = \
            RecordsStorage[_CollectionFieldTagLockRow](
                self._COLLECTION_FIELD_TAGS_STORAGE_PATH, time_provider,
                CollectionsManager._CollectionFieldTagsStorageProtocol())
        self._collection_items_storage = \
            RecordsStorage[_CollectionItemLockRow](
                self._COLLECTION_ITEMS_STORAGE_PATH, time_provider,
                CollectionsManager._CollectionItemsStorageProtocol())

    def __enter__(self) -> 'CollectionsManager':
        """Enter context."""
        self._collections_storage.initialize()
        self._collection_field_tags_storage.initialize()
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
            schema_properties: NotionCollectionSchemaProperties,
            view_schemas: Dict[str, JSONDictType]) -> NotionCollectionLink:
        """Create the Notion-side structure for this collection."""
        simdif_fields = set(schema.keys()).symmetric_difference(m.name for m in schema_properties)

        if len(simdif_fields) > 0:
            raise Exception(f"Schema params are off: {','.join(simdif_fields)}")

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

        # Arrange the fields.

        client.assign_collection_schema_properties(collection, schema_properties)
        LOGGER.info("Changed the field order")

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

    def load_collection(self, key: NotionLockKey) -> NotionCollectionLinkExtra:
        """Retrive the Notion-side structure for this collection."""
        lock = self._collections_storage.load(key)
        client = self._connection.get_notion_client()
        page = client.get_collection_page_by_id(lock.page_id)
        return NotionCollectionLinkExtra(
            page_id=lock.page_id,
            collection_id=lock.collection_id,
            name=page.title)

    def remove_collection(self, key: NotionLockKey) -> None:
        """Remove the Notion-side structure for this collection."""
        lock = self._collections_storage.load(key)
        client = self._connection.get_notion_client()

        page = client.get_collection_page_by_id(lock.page_id)
        page.remove()

        self._collections_storage.remove(key)

    def update_collection(self, key: NotionLockKey, new_name: str, new_schema: JSONDictType) -> None:
        """Just updates the name and schema for the collection and asks no questions."""
        lock = self._collections_storage.load(key)
        client = self._connection.get_notion_client()
        page = client.get_collection_page_by_id(lock.page_id)
        collection = client.get_collection(lock.page_id, lock.collection_id, lock.view_ids.values())
        page.title = new_name
        collection.name = new_name
        old_schema = collection.get("schema")
        final_schema = self._merge_notion_schemas(old_schema, new_schema)
        collection.set("schema", final_schema)
        LOGGER.info("Applied the most current schema to the collection")

    def update_collection_no_merge(self, key: NotionLockKey, new_name: str, new_schema: JSONDictType) -> None:
        """Just updates the name and schema for the collection and asks no questions."""
        lock = self._collections_storage.load(key)
        client = self._connection.get_notion_client()
        page = client.get_collection_page_by_id(lock.page_id)
        collection = client.get_collection(lock.page_id, lock.collection_id, lock.view_ids.values())
        page.title = new_name
        collection.name = new_name
        collection.set("schema", new_schema)
        LOGGER.info("Applied the most current schema to the collection")

    @staticmethod
    def _build_compound_key(collection_key: str, key: str) -> str:
        return f"{collection_key}:{key}"

    def upsert_collection_field_tag(
            self, collection_key: NotionLockKey, key: NotionLockKey, ref_id: EntityId,
            field: str, tag: str) -> _NotionCollectionTagLink:
        """Create a new tag for a Collection's field which has tags support."""
        collection_lock = self._collections_storage.load(collection_key)
        tag_key = self._build_compound_key(collection_key, key)
        lock = self._collection_field_tags_storage.load_optional(tag_key)

        client = self._connection.get_notion_client()
        collection = client.get_collection(
            collection_lock.page_id, collection_lock.collection_id, collection_lock.view_ids.values())
        schema = collection.get("schema")

        if field not in schema:
            raise Exception(f'Field "{field}" not in schema')

        field_schema = schema[field]

        if field_schema["type"] != "select" and field_schema["type"] != "multi_select":
            raise Exception(f'Field "{field}" is not appropriate for tags')

        if "options" not in field_schema:
            field_schema["options"] = []

        tag_id = None
        if lock:
            for option in field_schema["options"]:
                if option["id"] == lock.tag_id:
                    option["value"] = tag
                    option["color"] = self._get_stable_color(tag_key)
                    tag_id = lock.tag_id
                    LOGGER.info(f'Found tag "{tag}" ({lock.tag_id}) for field "{field}"')
                    break
            else:
                LOGGER.info(f'Could not find "{tag}" ({lock.tag_id})')

        if tag_id is None:
            tag_id = NotionId(str(uuid.uuid4()))
            field_schema["options"].append({
                "id": tag_id,
                "value": tag,
                "color": self._get_stable_color(tag_key)
            })
            LOGGER.info(f"Added new item for collection schema")

        collection.set("schema", schema)

        new_lock = _CollectionFieldTagLockRow(
            key=tag_key,
            collection_key=collection_key,
            tag_id=tag_id,
            field=field,
            ref_id=ref_id)

        if lock:
            self._collection_field_tags_storage.update(new_lock)
        else:
            self._collection_field_tags_storage.create(new_lock)
        LOGGER.info("Saved lock structure")

        return _NotionCollectionTagLink(
            notion_id=tag_id,
            collection_id=collection.id,
            name=tag,
            ref_id=ref_id)

    def load_all_collection_field_tags(
            self, collection_key: NotionLockKey, field: str) -> Iterable[_NotionCollectionTagLink]:
        """Load all tags for a field in a collection."""
        collection_lock = self._collections_storage.load(collection_key)

        client = self._connection.get_notion_client()
        collection = client.get_collection(
            collection_lock.page_id, collection_lock.collection_id, collection_lock.view_ids.values())
        schema = collection.get("schema")

        if field not in schema:
            raise Exception(f'Field "{field}" not in schema')

        field_schema = schema[field]

        if field_schema["type"] != "select" and field_schema["type"] != "multi_select":
            raise Exception(f'Field "{field}" is not appropriate for tags')

        if "options" not in field_schema:
            return []

        tag_links_lock_by_tag_id = {
            s.tag_id: s.ref_id
            for s in self._collection_field_tags_storage.find_all(collection_key=Eq(collection_key), field=Eq(field))}

        return [
            _NotionCollectionTagLink(
                collection_id=collection.id,
                notion_id=NotionId(option["id"]),
                name=option["value"],
                ref_id=tag_links_lock_by_tag_id.get(NotionId(option["id"]), None))
            for option in field_schema["options"]]

    def save_collection_field_tag(
            self, collection_key: NotionLockKey, key: NotionLockKey, ref_id: EntityId,
            field: str, tag: str) -> _NotionCollectionTagLink:
        """Create a new tag for a Collection's field which has tags support."""
        collection_lock = self._collections_storage.load(collection_key)
        tag_key = self._build_compound_key(collection_key, key)
        lock = self._collection_field_tags_storage.load(tag_key)

        client = self._connection.get_notion_client()
        collection = client.get_collection(
            collection_lock.page_id, collection_lock.collection_id, collection_lock.view_ids.values())
        schema = collection.get("schema")

        if field not in schema:
            raise Exception(f'Field "{field}" not in schema')

        field_schema = schema[field]

        if field_schema["type"] != "select" and field_schema["type"] != "multi_select":
            raise Exception(f'Field "{field}" is not appropriate for tags')

        if "options" not in field_schema:
            field_schema["options"] = []

        for option in field_schema["options"]:
            if option["id"] == lock.tag_id:
                option["value"] = tag
                option["color"] = self._get_stable_color(tag_key)
                tag_id = lock.tag_id
                LOGGER.info(f'Found tag "{tag}" ({lock.tag_id}) for field "{field}"')
                break
        else:
            raise Exception(f'Could not find "{tag}" ({lock.tag_id})')

        collection.set("schema", schema)

        new_lock = _CollectionFieldTagLockRow(
            key=tag_key,
            collection_key=collection_key,
            tag_id=tag_id,
            field=field,
            ref_id=ref_id)

        self._collection_field_tags_storage.update(new_lock)
        LOGGER.info("Saved lock structure")

        return _NotionCollectionTagLink(
            notion_id=tag_id,
            collection_id=collection.id,
            name=tag,
            ref_id=ref_id)

    def load_all_saved_collection_field_tag_notion_ids(
            self, collection_key: NotionLockKey, field: str) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids."""
        return [r.tag_id for r
                in self._collection_field_tags_storage.find_all(collection_key=Eq(collection_key), field=Eq(field))]

    def drop_all_collection_field_tags(self, collection_key: NotionLockKey, field: str) -> None:
        """Hard remove all the Notion-side entities."""
        collection_lock = self._collections_storage.load(collection_key)
        client = self._connection.get_notion_client()
        collection = client.get_collection(
            collection_lock.page_id, collection_lock.collection_id, collection_lock.view_ids.values())

        schema = collection.get("schema")

        if field not in schema:
            raise Exception(f'Field "{field}" not in schema')

        field_schema = schema[field]

        if field_schema["type"] != "select" and field_schema["type"] != "multi_select":
            raise Exception(f'Field "{field}" is not appropriate for tags')

        field_schema["options"] = []

        collection.set("schema", schema)

    def quick_link_local_and_notion_collection_field_tag(
            self, key: NotionLockKey, collection_key: NotionLockKey, field: str, ref_id: EntityId,
            notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        tag_key = self._build_compound_key(collection_key, key)
        lock = self._collection_field_tags_storage.load_optional(tag_key)

        new_lock = _CollectionFieldTagLockRow(
            key=tag_key,
            collection_key=collection_key,
            tag_id=notion_id,
            field=field,
            ref_id=ref_id)

        if lock is not None:
            LOGGER.warning(f"Entity already exists on Notion side for entity with id={ref_id}")
            self._collection_field_tags_storage.update(new_lock)
        else:
            self._collection_field_tags_storage.create(new_lock)

    def remove_collection_field_tag(self, key: NotionLockKey, collection_key: NotionLockKey) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        tag_key = self._build_compound_key(collection_key, key)
        collection_lock = self._collections_storage.load(collection_key)
        lock = self._collection_field_tags_storage.load(tag_key)
        client = self._connection.get_notion_client()
        collection = client.get_collection(
            collection_lock.page_id, collection_lock.collection_id, collection_lock.view_ids.values())

        schema = collection.get("schema")

        if lock.field not in schema:
            raise Exception(f'Field "{lock.field}" not in schema')

        field_schema = schema[lock.field]

        if field_schema["type"] != "select" and field_schema["type"] != "multi_select":
            raise Exception(f'Field "{lock.field}" is not appropriate for tags')

        if "options" not in field_schema:
            field_schema["options"] = []

        for option_idx, option in enumerate(field_schema["options"]):
            if option["id"] == lock.tag_id:
                del field_schema["options"][option_idx]
                LOGGER.info(f'Found tag {lock.tag_id} for field "{lock.field}"')
                break
        else:
            LOGGER.info(f'Could not find tag for {lock.tag_id}')

        collection.set("schema", schema)

        self._collection_field_tags_storage.remove(tag_key)

    def upsert_collection_item(
            self, collection_key: NotionLockKey, key: NotionLockKey, new_row: ItemType,
            copy_row_to_notion_row: CopyRowToNotionRowType[ItemType]) -> ItemType:
        """Create a Notion entity."""
        if new_row.ref_id is None:
            raise Exception("Can only create over an entity which has a ref_id")

        collection_lock = self._collections_storage.load(collection_key)
        item_key = self._build_compound_key(collection_key, key)
        lock = self._collection_items_storage.load_optional(item_key)

        client = self._connection.get_notion_client()
        collection = client.get_collection(
            collection_lock.page_id, collection_lock.collection_id, collection_lock.view_ids.values())

        was_found = False
        if lock:
            notion_row = client.get_collection_row(collection, lock.row_id)
            if notion_row.alive:
                was_found = True
                LOGGER.info(f"Entity already exists on Notion side with id={notion_row.id}")

        if not was_found:
            notion_row = client.create_collection_row(collection)
            LOGGER.info(f"Created new row on Notion side with id={notion_row.id}")

        new_row = dataclasses.replace(new_row, notion_id=notion_row.id)

        new_lock = _CollectionItemLockRow(
            key=item_key,
            collection_key=collection_key,
            row_id=notion_row.id,
            ref_id=EntityId.from_raw(new_row.ref_id))

        if lock:
            self._collection_items_storage.update(new_lock)
        else:
            self._collection_items_storage.create(new_lock)
        LOGGER.info("Saved local locks")

        copy_row_to_notion_row(client, new_row, notion_row)
        LOGGER.info(f"Created new entity with id {notion_row.id}")

        return new_row

    def quick_link_local_and_notion_entries_for_collection_item(
            self, key: NotionLockKey, collection_key: NotionLockKey, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""
        item_key = self._build_compound_key(collection_key, key)
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

    def quick_archive_collection_item(self, key: NotionLockKey, collection_key: NotionLockKey) -> None:
        """Remove a particular entity."""
        item_key = self._build_compound_key(collection_key, key)
        collection_lock = self._collections_storage.load(collection_key)
        lock = self._collection_items_storage.load(item_key)
        client = self._connection.get_notion_client()
        collection = client.get_collection(
            collection_lock.page_id, collection_lock.collection_id, collection_lock.view_ids.values())
        notion_row = client.get_collection_row(collection, lock.row_id)
        notion_row.archived = True

    def load_all_collection_items(
            self, collection_key: NotionLockKey,
            copy_notion_row_to_row: CopyNotionRowToRowType[ItemType]) -> Iterable[ItemType]:
        """Retrieve all the Notion-side entitys."""
        collection_lock = self._collections_storage.load(collection_key)
        client = self._connection.get_notion_client()
        collection = client.get_collection(
            collection_lock.page_id, collection_lock.collection_id, collection_lock.view_ids.values())
        all_notion_rows = client.get_collection_all_rows(collection, collection_lock.view_ids["database_view_id"])

        return [copy_notion_row_to_row(nr) for nr in all_notion_rows]

    def load_collection_item(
            self, key: NotionLockKey, collection_key: NotionLockKey,
            copy_notion_row_to_row: CopyNotionRowToRowType[ItemType]) -> ItemType:
        """Retrieve the Notion-side entity associated with a particular entity."""
        item_key = self._build_compound_key(collection_key, key)
        collection_lock = self._collections_storage.load(collection_key)
        lock = self._collection_items_storage.load(item_key)
        client = self._connection.get_notion_client()
        collection = client.get_collection(collection_lock.page_id, collection_lock.collection_id,
                                           collection_lock.view_ids.values())
        notion_row = client.get_collection_row(collection, lock.row_id)
        return copy_notion_row_to_row(notion_row)

    def save_collection_item(
            self, key: NotionLockKey, collection_key: NotionLockKey, row: ItemType,
            copy_row_to_notion_row: CopyRowToNotionRowType[ItemType]) -> ItemType:
        """Update the Notion-side entity with new data."""
        if row.ref_id is None:
            raise Exception("Can only save over an entity which has a ref_id")

        item_key = self._build_compound_key(collection_key, key)
        collection_lock = self._collections_storage.load(collection_key)
        lock = self._collection_items_storage.load(item_key)
        client = self._connection.get_notion_client()
        collection = client.get_collection(collection_lock.page_id, collection_lock.collection_id,
                                           collection_lock.view_ids.values())
        notion_row = client.get_collection_row(collection, lock.row_id)
        copy_row_to_notion_row(client, row, notion_row)

        return row

    def load_all_collection_items_saved_notion_ids(self, collection_key: NotionLockKey) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids."""
        return [r.row_id for r
                in self._collection_items_storage.find_all(collection_key=Eq(collection_key))]

    def load_all_collection_items_saved_ref_ids(self, collection_key: NotionLockKey) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids."""
        return [r.ref_id for r
                in self._collection_items_storage.find_all(collection_key=Eq(collection_key))]

    def drop_all_collection_items(self, collection_key: NotionLockKey) -> None:
        """Hard remove all the Notion-side entities."""
        collection_lock = self._collections_storage.load(collection_key)
        client = self._connection.get_notion_client()
        collection = client.get_collection(
            collection_lock.page_id, collection_lock.collection_id, collection_lock.view_ids.values())

        all_notion_rows = client.get_collection_all_rows(collection, collection_lock.view_ids["database_view_id"])

        for notion_row in all_notion_rows:
            notion_row.remove()

        for item in self._collection_items_storage.find_all(collection_key=Eq(collection_key)):
            self._collection_items_storage.remove(item.key)

    def remove_collection_item(self, key: NotionLockKey, collection_key: NotionLockKey) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        item_key = self._build_compound_key(collection_key, key)
        collection_lock = self._collections_storage.load(collection_key)
        try:
            lock = self._collection_items_storage.load(item_key)
            client = self._connection.get_notion_client()
            collection = client.get_collection(collection_lock.page_id, collection_lock.collection_id,
                                               collection_lock.view_ids.values())
            notion_row = client.get_collection_row(collection, lock.row_id)
            notion_row.remove()
            self._collection_items_storage.remove(item_key)
        except StructuredStorageError:
            LOGGER.error(
                f"Tried to hard remove Notion-side entity identified by {collection_key}:{key} but found nothing")

    @staticmethod
    def _merge_notion_schemas(old_schema: JSONDictType, new_schema: JSONDictType) -> JSONDictType:
        """Merge an old and new schema for the collection."""
        old_schema_any: typing.Any = old_schema # type: ignore
        new_schema_any: typing.Any = new_schema # type: ignore
        combined_schema = {}

        # Merging schema is limited right now. Basically we assume the new schema takes
        # precedence over the old one, except for select and multi_select, which have a set
        # of options for them which are identified by "id"s. We wanna keep these stable
        # across schema updates.
        # As a special case, the big plan item is left to whatever value it had before
        # since this thing is managed via the big plan syncing flow!
        # As another special case, the recurring tasks group key is left to whatever value it had
        # before since this thing is managed by the other flows!
        for (schema_item_name, schema_item) in new_schema_any.items():
            if schema_item_name == "bigplan2":
                combined_schema[schema_item_name] = old_schema_any[schema_item_name] \
                    if (schema_item_name in old_schema_any and old_schema_any[schema_item_name]["type"] == "select") \
                    else schema_item
            elif schema_item["type"] == "select" or schema_item["type"] == "multi_select":
                if schema_item_name in old_schema_any:
                    old_v = old_schema_any[schema_item_name]

                    combined_schema[schema_item_name] = {
                        "name": schema_item["name"],
                        "type": schema_item["type"],
                        "options": typing.cast(typing.List[Dict[str, str]], old_v.get("options", []))
                    }

                    for option in schema_item["options"]:
                        old_option = next(
                            (old_o
                             for old_o in combined_schema[schema_item_name]["options"]
                             if old_o["value"] == option["value"]),
                            None)
                        if old_option is not None:
                            old_option["color"] = option["color"]
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

    class _CollectionFieldTagsStorageProtocol:
        @staticmethod
        def storage_schema() -> JSONDictType:
            """The schema for the data."""
            return {
                "key": {"type": "string"},
                "collection_key": {"type": "string"},
                "ref_id": {"type": "string"},
                "field": {"type": "string"},
                "tag_id": {"type": "string"}
            }

        @staticmethod
        def storage_to_live(storage_form: JSONDictType) -> _CollectionFieldTagLockRow:
            """Transform the data reconstructed from basic storage into something useful for the live system."""
            return _CollectionFieldTagLockRow(
                key=NotionLockKey(typing.cast(str, storage_form["key"])),
                collection_key=NotionLockKey(typing.cast(str, storage_form["collection_key"])),
                ref_id=EntityId.from_raw(typing.cast(str, storage_form["ref_id"])),
                field=typing.cast(str, storage_form["field"]),
                tag_id=NotionId(typing.cast(str, storage_form["tag_id"])))

        @staticmethod
        def live_to_storage(live_form: _CollectionFieldTagLockRow) -> JSONDictType:
            """Transform the live system data to something suitable for basic storage."""
            return {
                "collection_key": live_form.collection_key,
                "ref_id": str(live_form.ref_id),
                "tag_id": live_form.tag_id,
                "field": live_form.field
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
            if not storage_form["ref_id"]:
                LOGGER.error(storage_form)
            return _CollectionItemLockRow(
                key=NotionLockKey(typing.cast(str, storage_form["key"])),
                collection_key=NotionLockKey(typing.cast(str, storage_form["collection_key"])),
                ref_id=EntityId.from_raw(typing.cast(str, storage_form["ref_id"])),
                row_id=NotionId(typing.cast(str, storage_form["row_id"])))

        @staticmethod
        def live_to_storage(live_form: _CollectionItemLockRow) -> JSONDictType:
            """Transform the live system data to something suitable for basic storage."""
            return {
                "collection_key": live_form.collection_key,
                "ref_id": str(live_form.ref_id),
                "row_id": live_form.row_id
            }

    @staticmethod
    def _get_stable_color(option_id: str) -> str:
        """Return a random-ish yet stable color for a given name."""
        colors = [
            "gray",
            "brown",
            "orange",
            "yellow",
            "green",
            "blue",
            "purple",
            "pink",
            "red"
        ]
        return colors[hashlib.sha256(option_id.encode("utf-8")).digest()[0] % len(colors)]

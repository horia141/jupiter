"""A generic Notion collection as understood by Jupiter."""
import logging
from dataclasses import field, dataclass
from pathlib import Path
from typing import TypeVar, Generic, Final, Dict, Any, Protocol, List, Optional, Iterable, cast

from notion.collection import CollectionRowBlock

from models.basic import EntityId
from remote.notion.client import NotionClient
from remote.notion.common import NotionId, NotionPageLink, NotionCollectionLink, CollectionError, \
    CollectionEntityNotFound
from remote.notion.connection import NotionConnection
from utils.storage import StructuredCollectionStorage, JSONDictType

LOGGER = logging.getLogger(__name__)


@dataclass()
class BasicRowType:
    """A basic row type, which must contain a Notion id and an local id."""

    notion_id: NotionId
    ref_id: Optional[str]


NotionCollectionRowType = TypeVar("NotionCollectionRowType", bound=BasicRowType)
NotionCollectionKWArgsType = Any  # type: ignore # pylint: disable=invalid-name


class NotionCollectionProtocol(Protocol[NotionCollectionRowType]):
    """Protocol for clients of StructuredIndividualStorage to expose."""

    @staticmethod
    def get_page_name() -> str:
        """Get the name for the page."""
        ...

    @staticmethod
    def get_notion_schema() -> JSONDictType:
        """Get the Notion schema for the collection."""
        ...

    @staticmethod
    def merge_notion_schemas(_old_schema: JSONDictType, _new_schema: JSONDictType) -> JSONDictType:
        """Merge an old and new schema for the collection."""
        ...

    @staticmethod
    def get_view_schemas() -> Dict[str, JSONDictType]:
        """Get the Notion view schemas for the collection."""
        ...

    def copy_row_to_notion_row(
            self, client: NotionClient, row: NotionCollectionRowType, notion_row: CollectionRowBlock,
            **kwargs: NotionCollectionKWArgsType) -> CollectionRowBlock:
        """Copy the fields of the local row to the actual Notion structure."""
        # pylint: disable=unused-argument
        # pylint: disable=no-self-use
        ...

    def copy_notion_row_to_row(self, notion_row: CollectionRowBlock) -> NotionCollectionRowType:
        """Transform the live system data to something suitable for basic storage."""
        # pylint: disable=unused-argument
        # pylint: disable=no-self-use
        ...


@dataclass()
class NotionCollectionLock:
    """The lock contains information about the associated Notion entities."""

    discriminant: str
    page_id: NotionId
    collection_id: NotionId
    view_ids: Dict[str, NotionId] = field(default_factory=dict, compare=False)
    ref_id_to_notion_id_map: Dict[EntityId, NotionId] = field(
        default_factory=dict, repr=False, hash=False, compare=False)


class NotionCollection(Generic[NotionCollectionRowType]):
    """A generic Notion collection as understood by Jupiter."""

    _connection: Final[NotionConnection]
    _structured_storage: Final[StructuredCollectionStorage[NotionCollectionLock]]
    _protocol: NotionCollectionProtocol[NotionCollectionRowType]  # Really final here.

    def __init__(
            self, connection: NotionConnection, storage_path: Path,
            protocol: NotionCollectionProtocol[NotionCollectionRowType]) -> None:
        """Constructor."""
        self._connection = connection
        self._structured_storage = StructuredCollectionStorage(storage_path, self)
        self._protocol = protocol

    def initialize(self) -> None:
        """Initialise the collection storage."""
        self._structured_storage.initialize()

    def exit_save(self) -> None:
        """Save everything at the end."""
        self._structured_storage.exit_save()

    def upsert_structure(self, discriminant: str, parent_page: NotionPageLink) -> NotionCollectionLink:
        """Create the Notion-side structure for this collection."""
        locks_next_idx, locks = self._structured_storage.load()
        lock = self._find_lock(locks, discriminant)

        client = self._connection.get_notion_client()

        if lock:
            page = client.get_collection_page_by_id(lock.page_id)
            LOGGER.info(f"Found the already existing page as {page.id}")
            collection = client.get_collection(lock.page_id, lock.collection_id, lock.view_ids.values())
            LOGGER.info(f"Found the already existing collection {collection.id}")
        else:
            page = client.create_collection_page(parent_page=client.get_regular_page(parent_page.page_id))
            LOGGER.info(f"Created the page as {page.id}")
            collection = client.create_collection(page, self._protocol.get_notion_schema())
            LOGGER.info(f"Created the collection as {collection}")

        # Change the schema.

        old_collection_schema = collection.get("schema")
        collection_schema = self._protocol.merge_notion_schemas(
            old_collection_schema, self._protocol.get_notion_schema())
        collection.set("schema", collection_schema)
        LOGGER.info("Applied the most current schema to the collection")

        # Attach the views.
        view_ids = lock.view_ids if lock else {}
        for view_name, view_schema in self._protocol.get_view_schemas().items():
            the_view = client.attach_view_to_collection_page(
                page, collection, view_ids.get(view_name, None), cast(str, view_schema["type"]), view_schema)
            view_ids[view_name] = the_view.id
            LOGGER.info(f"Attached view '{view_name}' to collection id='{collection.id}'")

        # Tie everything up.

        page.set("collection_id", collection.id)
        page.set("view_ids", list(view_ids.values()))

        # Change the title.

        page.title = self._protocol.get_page_name()
        collection.name = self._protocol.get_page_name()
        LOGGER.info("Changed the name")

        # Save local locks.
        new_lock = NotionCollectionLock(
            discriminant=discriminant,
            page_id=page.id,
            collection_id=collection.id,
            view_ids=view_ids,
            ref_id_to_notion_id_map=lock.ref_id_to_notion_id_map if lock else {})
        if lock:
            # Just replace the old value with the new one here.
            locks = [(itl if itl.discriminant != discriminant else new_lock) for itl in locks]
        else:
            # Add new value at the end here.
            locks.append(new_lock)
            locks_next_idx += 1
        self._structured_storage.save((locks_next_idx, locks))
        LOGGER.info("Saved lock structure")

        return NotionCollectionLink(page_id=page.id, collection_id=collection.id)

    def remove_structure(self, discriminant: str) -> None:
        """Remove the Notion-side structure for this collection."""
        locks_next_idx, locks = self._structured_storage.load()
        lock = self._find_lock(locks, discriminant)

        if lock is None:
            raise CollectionError(f"Notion collection for discriminant '{discriminant}' does not exist")

        client = self._connection.get_notion_client()

        page = client.get_collection_page_by_id(lock.page_id)
        page.remove()

        new_locks = [l for l in locks if l.discriminant != discriminant]
        self._structured_storage.save((locks_next_idx, new_locks))

    def get_structure(self, discriminant: str) -> NotionCollectionLink:
        """Retrive the Notion-side structure for this collection."""
        _, locks = self._structured_storage.load()
        lock = self._find_lock(locks, discriminant)

        if lock is None:
            raise CollectionError(f"Notion collection for discriminant '{discriminant}' does not exist")

        return NotionCollectionLink(page_id=lock.page_id, collection_id=lock.collection_id)

    def update_schema(self, discriminant: str, new_schema: JSONDictType) -> None:
        """Just updates the schema for the collection and asks no questions."""
        locks_next_idx, locks = self._structured_storage.load()
        lock = self._find_lock(locks, discriminant)

        if lock is None:
            raise CollectionError(f"Notion collection for discriminant '{discriminant}' does not exist")

        client = self._connection.get_notion_client()

        client.update_collection_schema(lock.page_id, lock.collection_id, new_schema)

    def create(
            self, discriminant: str, new_row: NotionCollectionRowType,
            **kwargs: NotionCollectionKWArgsType) -> NotionCollectionRowType:
        """Create a Notion entity."""
        if new_row.ref_id is None:
            raise Exception("Can only create over an entity which has a ref_id")

        locks_next_idx, locks = self._structured_storage.load()
        lock = self._find_lock(locks, discriminant)

        if lock is None:
            raise CollectionError(f"Notion collection for discriminant '{discriminant}' does not exist")

        if new_row.ref_id in lock.ref_id_to_notion_id_map:
            raise CollectionError(f"Entity already exists on Notion side for entty with id={new_row.ref_id}")

        client = self._connection.get_notion_client()
        collection = client.get_collection(lock.page_id, lock.collection_id, lock.view_ids.values())

        new_notion_row = client.create_collection_row(collection)

        new_row.notion_id = new_notion_row.id

        lock.ref_id_to_notion_id_map[EntityId(new_row.ref_id)] = new_notion_row.id
        self._structured_storage.save((locks_next_idx, locks))
        LOGGER.info("Saved local locks")

        self._protocol.copy_row_to_notion_row(client, new_row, new_notion_row, **kwargs)
        LOGGER.info(f"Created new entity with id {new_notion_row.id}")

        return new_row

    def link_local_and_notion_entries(self, discriminant: str, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notio none, useful in syncing processes."""
        locks_next_idx, task_locks = self._structured_storage.load()
        lock = self._find_lock(task_locks, discriminant)
        if lock is None:
            raise CollectionError(f"Notion collection for discriminant '{discriminant}' does not exist")
        if ref_id in lock.ref_id_to_notion_id_map:
            raise CollectionError(f"Entity already exists on Notion side for id={ref_id}")
        lock.ref_id_to_notion_id_map[ref_id] = notion_id
        self._structured_storage.save((locks_next_idx, task_locks))

    def archive(self, discriminant: str, ref_id: EntityId) -> None:
        """Remove a particular entity."""
        _, locks = self._structured_storage.load()
        lock = self._find_lock(locks, discriminant)
        if lock is None:
            raise CollectionError(f"Notion collection for discriminant '{discriminant}' does not exist")
        client = self._connection.get_notion_client()
        inbox_task_notion_row = self._find_notion_row(client, lock, ref_id)

        inbox_task_notion_row.archived = True

    def load_all(self, discriminant: str) -> Iterable[NotionCollectionRowType]:
        """Retrieve all the Notion-side entitys."""
        _, locks = self._structured_storage.load()
        lock = self._find_lock(locks, discriminant)
        if lock is None:
            raise CollectionError(f"Notion collection for discriminant '{discriminant}' does not exist")
        client = self._connection.get_notion_client()
        collection = client.get_collection(lock.page_id, lock.collection_id, lock.view_ids.values())
        all_notion_rows = client.get_collection_all_rows(collection, lock.view_ids["database_view_id"])

        return [self._protocol.copy_notion_row_to_row(nr) for nr in all_notion_rows]

    def load(self, discriminant: str, ref_id: EntityId) -> NotionCollectionRowType:
        """Retrieve the Notion-side entity associated with a particular entity."""
        _, locks = self._structured_storage.load()
        lock = self._find_lock(locks, discriminant)
        if lock is None:
            raise CollectionError(f"Notion collection for discriminant '{discriminant}' does not exist")
        client = self._connection.get_notion_client()
        inbox_task_notion_row = self._find_notion_row(client, lock, ref_id)

        return self._protocol.copy_notion_row_to_row(inbox_task_notion_row)

    def save(
            self, discriminant: str, row: NotionCollectionRowType,
            **kwargs: NotionCollectionKWArgsType) -> NotionCollectionRowType:
        """Update the Notion-side entity with new data."""
        if row.ref_id is None:
            raise Exception("Can only save over an entity which has a ref_id")

        _, locks = self._structured_storage.load()
        lock = self._find_lock(locks, discriminant)
        if lock is None:
            raise CollectionError(f"Notion collection for discriminant '{discriminant}' does not exist")
        client = self._connection.get_notion_client()
        notion_row = self._find_notion_row(client, lock, EntityId(row.ref_id))

        self._protocol.copy_row_to_notion_row(client, row, notion_row, **kwargs)

        return row

    def load_all_saved_notion_ids(self, discriminant: str) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids."""
        _, locks = self._structured_storage.load()
        lock = self._find_lock(locks, discriminant)
        if lock is None:
            raise CollectionError(f"Notion collection for discriminant '{discriminant}' does not exist")
        return lock.ref_id_to_notion_id_map.values()

    def drop_all(self, discriminant: str) -> None:
        """Hard remove all the Notion-side entities."""
        locks_next_idx, locks = self._structured_storage.load()
        lock = self._find_lock(locks, discriminant)
        if lock is None:
            raise CollectionError(f"Notion collection for discriminant '{discriminant}' does not exist")
        client = self._connection.get_notion_client()
        collection = client.get_collection(lock.page_id, lock.collection_id, lock.view_ids.values())

        all_notion_rows = client.get_collection_all_rows(collection, lock.view_ids["database_view_id"])

        for notion_row in all_notion_rows:
            notion_row.remove()

        lock.ref_id_to_notion_id_map = {}
        self._structured_storage.save((locks_next_idx, locks))

    def hard_remove(self, discriminant: str, notion_id: NotionId, ref_id: Optional[EntityId]) -> None:
        """Hard remove the Notion entity associated with a local entity."""
        locks_next_idx, locks = self._structured_storage.load()
        lock = self._find_lock(locks, discriminant)
        if lock is None:
            raise CollectionError(f"Notion collection for discriminant '{discriminant}' does not exist")
        client = self._connection.get_notion_client()

        collection = client.get_collection(lock.page_id, lock.collection_id, lock.view_ids.values())

        notion_row = client.get_collection_row(collection, notion_id)
        notion_row.remove()

        if ref_id in lock.ref_id_to_notion_id_map:
            del lock.ref_id_to_notion_id_map[ref_id]
            self._structured_storage.save((locks_next_idx, locks))

    @staticmethod
    def _find_lock(locks: List[NotionCollectionLock], discriminant: str) -> Optional[NotionCollectionLock]:
        return next((itl for itl in locks if itl.discriminant == discriminant), None)

    @staticmethod
    def _find_notion_row(
            client: NotionClient, lock: NotionCollectionLock, ref_id: EntityId) -> CollectionRowBlock:
        collection = client.get_collection(lock.page_id, lock.collection_id, lock.view_ids.values())

        if ref_id in lock.ref_id_to_notion_id_map:
            try:
                LOGGER.info(f"Finding by stored id")
                notion_row = client.get_collection_row(collection, lock.ref_id_to_notion_id_map[ref_id])
                return notion_row
            except IOError:
                pass

        LOGGER.info(f"Finding by ref_id search")
        all_notion_rows = client.get_collection_all_rows(collection, lock.view_ids["database_view_id"])
        notion_row = next((vnr for vnr in all_notion_rows if vnr.ref_id == ref_id), None)

        if notion_row is None:
            raise CollectionEntityNotFound(f"Could not find Notion row with ref_id={ref_id}")

        return notion_row

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema of the data for this structure storage, as meant for basic storage."""
        return {
            "type": "object",
            "properties": {
                "page_id": {"type": "string"},
                "collection_id": {"type": "string"},
                "view_ids": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                },
                "ref_id_to_notion_map": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                }
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> NotionCollectionLock:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return NotionCollectionLock(
            discriminant=cast(str, storage_form["discriminant"]),
            page_id=NotionId(cast(str, storage_form["page_id"])),
            collection_id=NotionId(cast(str, storage_form["collection_id"])),
            view_ids={k: NotionId(v) for (k, v) in cast(Dict[str, str], storage_form["view_ids"]).items()},
            ref_id_to_notion_id_map={EntityId(k): NotionId(v)
                                     for (k, v)
                                     in cast(Dict[str, str], storage_form["ref_id_to_notion_id_map"]).items()})

    @staticmethod
    def live_to_storage(live_form: NotionCollectionLock) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "discriminant": live_form.discriminant,
            "page_id": live_form.page_id,
            "collection_id": live_form.collection_id,
            "view_ids": live_form.view_ids,
            "ref_id_to_notion_id_map": {str(k): str(v) for (k, v) in live_form.ref_id_to_notion_id_map.items()}
        }

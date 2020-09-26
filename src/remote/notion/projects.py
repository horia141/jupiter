"""The collection for vacations."""
import logging
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Final, ClassVar, List, Optional, Type, cast

from models.basic import EntityId
from remote.notion.common import NotionId, NotionPageLink, CollectionError, CollectionEntityNotFound, \
    CollectionEntityAlreadyExists
from remote.notion.infra.connection import NotionConnection
from utils.storage import StructuredCollectionStorage, JSONDictType

LOGGER = logging.getLogger(__name__)


@dataclass()
class ProjectScreen:
    """A project on Notion side."""

    name: str
    notion_id: NotionId
    ref_id: EntityId


@dataclass()
class ProjectLock:
    """The lock contains information about the associated Notion entities."""
    page_id: NotionId
    ref_id: EntityId


class ProjectsCollection:
    """A collection on Notion side for projects."""

    _LOCK_FILE_PATH: ClassVar[Path] = Path("/data/projects.lock.yaml")

    _connection: Final[NotionConnection]
    _structured_storage: Final[StructuredCollectionStorage[ProjectLock]]

    def __init__(self, connection: NotionConnection) -> None:
        """Create a project."""
        self._connection = connection
        self._structured_storage = StructuredCollectionStorage(self._LOCK_FILE_PATH, self)

    def __enter__(self) -> 'ProjectsCollection':
        """Enter context."""
        self._structured_storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return
        self._structured_storage.exit_save()

    def get_project_page_structure(self, ref_id: EntityId) -> NotionPageLink:
        """Retrieve the Notion-side structure link for this collection."""
        _, locks = self._structured_storage.load()
        lock = self._find_lock(locks, ref_id)

        if lock is None:
            raise CollectionEntityAlreadyExists(f"Entity with id='{ref_id}' already exists on Notion side")

        return NotionPageLink(page_id=lock.page_id)

    def create_project(self, name: str, ref_id: EntityId, parent_page: NotionPageLink) -> ProjectScreen:
        """Create a project on Notion side."""
        locks_next_idx, locks = self._structured_storage.load()
        lock = self._find_lock(locks, ref_id)

        if lock is not None:
            raise CollectionEntityAlreadyExists(f"Entity with id='{ref_id}' already exists on Notion side")

        client = self._connection.get_notion_client()

        new_page = client.create_regular_page(name, client.get_regular_page(parent_page.page_id))

        new_lock = ProjectLock(
            page_id=new_page.id,
            ref_id=ref_id)
        locks.append(new_lock)
        self._structured_storage.save((locks_next_idx + 1, locks))
        LOGGER.info("Saved lock structure")

        return ProjectScreen(
            name=name,
            notion_id=new_page.id,
            ref_id=ref_id)

    def archive_project(self, ref_id: EntityId) -> None:
        """Remove a project on Notion side."""
        locks_next_idx, locks = self._structured_storage.load()
        lock = self._find_lock(locks, ref_id)

        if not lock:
            raise CollectionEntityNotFound(f"Entity with id='{ref_id} does not exist")

        client = self._connection.get_notion_client()

        page = client.get_regular_page(lock.page_id)
        page.remove()

        new_locks = [l for l in locks if l.ref_id != ref_id]
        self._structured_storage.save((locks_next_idx, new_locks))

    def load_project(self, ref_id: EntityId) -> ProjectScreen:
        """Retrieve a project from Notion via id."""
        _, locks = self._structured_storage.load()
        lock = self._find_lock(locks, ref_id)

        if not lock:
            raise CollectionError(f"Entity with id='{ref_id} does not exist")

        client = self._connection.get_notion_client()

        page = client.get_regular_page(lock.page_id)

        return ProjectScreen(name=page.title, notion_id=page.id, ref_id=lock.ref_id)

    def save_project(self, new_project_screen: ProjectScreen) -> ProjectScreen:
        """Save the Notion structure."""
        _, locks = self._structured_storage.load()
        lock = self._find_lock(locks, new_project_screen.ref_id)

        if not lock:
            raise CollectionError(f"Entity with id='{new_project_screen.ref_id} does not exist")

        client = self._connection.get_notion_client()

        page = client.get_regular_page(lock.page_id)
        page.title = new_project_screen.name

        return ProjectScreen(name=new_project_screen.name, notion_id=new_project_screen.notion_id, ref_id=lock.ref_id)

    @staticmethod
    def _find_lock(locks: List[ProjectLock], ref_id: EntityId) -> Optional[ProjectLock]:
        return next((l for l in locks if l.ref_id == ref_id), None)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "type": "object",
            "properties": {
                "page_id": {"type": "string"},
                "ref_id": {"type": "string"}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> ProjectLock:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return ProjectLock(
            page_id=NotionId(cast(str, storage_form["page_id"])),
            ref_id=EntityId(cast(str, storage_form["ref_id"])))

    @staticmethod
    def live_to_storage(live_form: ProjectLock) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "page_id": live_form.page_id,
            "ref_id": live_form.ref_id
        }

"""The singleton for workspaces."""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Final, cast

from domain.common.entity_name import EntityName
from remote.notion.common import CollectionError, NotionPageLink
from remote.notion.infra.connection import NotionConnection
from utils.storage import StructuredIndividualStorage
from models.framework import JSONDictType, NotionId

LOGGER = logging.getLogger(__name__)


class MissingWorkspaceScreenError(CollectionError):
    """Error raised when a workspace screen has not yet been created."""


@dataclass()
class WorkspaceScreen:
    """The workspace screen on Notion side."""

    name: str


@dataclass()
class WorkspaceLock:
    """Link to Notion-side entities for the workspace."""

    page_id: NotionId


class WorkspaceSingleton:
    """A single structure on Notion side for vacations."""

    _WORKSPACES_LOCK_FILE_PATH: ClassVar[Path] = Path("./workspaces.lock.yaml")

    _connection: Final[NotionConnection]
    _structured_storage: Final[StructuredIndividualStorage[WorkspaceLock]]

    def __init__(self, connection: NotionConnection) -> None:
        """Constructor."""
        self._connection = connection
        self._structured_storage = StructuredIndividualStorage(self._WORKSPACES_LOCK_FILE_PATH, self)

    def upsert_notion_structure(self, name: EntityName) -> NotionPageLink:
        """Create/update the Notion-side structure for this singleton."""
        lock = self._structured_storage.load_optional()
        client = self._connection.get_notion_client()

        if lock:
            page = client.get_regular_page(lock.page_id)
            LOGGER.info(f"Found the root page via id {page}")
        else:
            page = client.create_regular_page(str(name))
            LOGGER.info(f"Created the root page {page}")

        # Change the title.
        page.title = str(name)
        LOGGER.info("Applied changes to root page on Notion side")

        # Saved local locks.

        new_lock = WorkspaceLock(page_id=page.id)
        self._structured_storage.save(new_lock)
        LOGGER.info("Saved lock structure")

        return NotionPageLink(page_id=page.id)

    def get_notion_structure(self) -> NotionPageLink:
        """Retrieve the Notion-side structure link."""
        lock = self._structured_storage.load_optional()

        if not lock:
            raise MissingWorkspaceScreenError()

        return NotionPageLink(page_id=lock.page_id)

    def load_workspace_screen(self) -> WorkspaceScreen:
        """Retrieve the Notion workspace representation."""
        lock = self._structured_storage.load_optional()
        if lock is None:
            raise MissingWorkspaceScreenError()

        client = self._connection.get_notion_client()

        page = client.get_regular_page(lock.page_id)

        return WorkspaceScreen(name=page.title)

    def save_workspace_screen(self, new_workspace_screen: WorkspaceScreen) -> WorkspaceScreen:
        """Update the Notion workspace with new data."""
        lock = self._structured_storage.load()
        client = self._connection.get_notion_client()

        page = client.get_regular_page(lock.page_id)

        page.title = new_workspace_screen.name

        return new_workspace_screen

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema of the data for this structure storage, as meant for basic storage."""
        return {
            "type": "object",
            "properties": {
                "page_id": {"type": "string"}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> WorkspaceLock:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return WorkspaceLock(page_id=NotionId(cast(str, storage_form["page_id"])))

    @staticmethod
    def live_to_storage(live_form: WorkspaceLock) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "page_id": live_form.page_id
        }

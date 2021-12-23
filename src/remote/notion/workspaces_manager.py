"""The singleton for workspaces."""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Final, cast

from domain.workspaces.infra.workspace_notion_manager import WorkspaceNotionManager
from domain.workspaces.notion_workspace import NotionWorkspace
from domain.workspaces.workspace import Workspace
from framework.json import JSONDictType
from framework.base.entity_id import EntityId
from framework.notion import NotionId
from remote.notion.common import CollectionError
from remote.notion.infra.connection import NotionConnection
from repository.yaml.infra.storage import StructuredIndividualStorage

LOGGER = logging.getLogger(__name__)


class MissingWorkspaceScreenError(CollectionError):
    """Error raised when a workspace screen has not yet been created."""


@dataclass()
class _WorkspaceLock:
    """Link to Notion-side entities for the workspace."""

    ref_id: EntityId
    page_id: NotionId


class NotionWorkspacesManager(WorkspaceNotionManager):
    """A single structure on Notion side for vacations."""

    _WORKSPACES_LOCK_FILE_PATH: ClassVar[Path] = Path("./workspaces.lock.yaml")

    _connection: Final[NotionConnection]
    _structured_storage: Final[StructuredIndividualStorage[_WorkspaceLock]]

    def __init__(self, connection: NotionConnection) -> None:
        """Constructor."""
        self._connection = connection
        self._structured_storage = StructuredIndividualStorage(self._WORKSPACES_LOCK_FILE_PATH, self)

    def upsert_workspace(self, workspace: Workspace) -> NotionWorkspace:
        """Upsert the root Notion structure."""
        lock = self._structured_storage.load_optional()
        client = self._connection.get_notion_client()

        if lock:
            page = client.get_regular_page(lock.page_id)
            LOGGER.info(f"Found the root page via id {page}")
        else:
            page = client.create_regular_page(str(workspace.name))
            LOGGER.info(f"Created the root page {page}")

        # Change the title.
        page.title = str(workspace.name)
        LOGGER.info("Applied changes to root page on Notion side")

        # Saved local locks.

        new_lock = _WorkspaceLock(ref_id=workspace.ref_id, page_id=page.id)
        self._structured_storage.save(new_lock)
        LOGGER.info("Saved lock structure")

        return NotionWorkspace(
            name=str(workspace.name),
            notion_id=page.id,
            ref_id=workspace.ref_id)

    def save_workspace(self, notion_workspace: NotionWorkspace) -> NotionWorkspace:
        """Change the root Notion structure."""
        lock = self._structured_storage.load()
        client = self._connection.get_notion_client()

        page = client.get_regular_page(lock.page_id)
        LOGGER.info(f"Found the root page via id {page}")

        # Change the title.
        page.title = notion_workspace.name
        LOGGER.info("Applied changes to root page on Notion side")

        return notion_workspace

    def load_workspace(self) -> NotionWorkspace:
        """Retrieve the workspace from Notion side."""
        lock = self._structured_storage.load_optional()
        if lock is None:
            raise MissingWorkspaceScreenError()

        client = self._connection.get_notion_client()

        page = client.get_regular_page(lock.page_id)

        return NotionWorkspace(
            name=page.title,
            notion_id=page.id,
            ref_id=lock.ref_id)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema of the data for this structure storage, as meant for basic storage."""
        return {
            "type": "object",
            "properties": {
                "ref_id": {"type": "string"},
                "page_id": {"type": "string"}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _WorkspaceLock:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _WorkspaceLock(
            ref_id=EntityId.from_raw(cast(str, storage_form["ref_id"])),
            page_id=NotionId(cast(str, storage_form["page_id"])))

    @staticmethod
    def live_to_storage(live_form: _WorkspaceLock) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "ref_id": str(live_form.ref_id),
            "page_id": str(live_form.page_id)
        }

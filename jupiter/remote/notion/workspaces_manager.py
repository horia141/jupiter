"""The centralised point for interacting with Notion workspaces."""
import logging
from typing import ClassVar, Final

from jupiter.domain.workspaces.infra.workspace_notion_manager import WorkspaceNotionManager, \
    NotionWorkspaceNotFoundError
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.pages_manager import NotionPagesManager, NotionPageNotFoundError

LOGGER = logging.getLogger(__name__)


class NotionWorkspacesManager(WorkspaceNotionManager):
    """The centralised point for interacting with Notion workspaces."""

    _KEY: ClassVar[str] = "workspaces"

    _pages_manager: Final[NotionPagesManager]

    def __init__(self, pages_manager: NotionPagesManager) -> None:
        """Constructor."""
        self._pages_manager = pages_manager

    def upsert_workspace(self, workspace: NotionWorkspace) -> NotionWorkspace:
        """Upsert the root Notion structure."""
        workspace_page = self._pages_manager.upsert_page(NotionLockKey(self._KEY), workspace.name)

        return NotionWorkspace(
            name=workspace.name,
            notion_id=workspace_page.notion_id,
            ref_id=workspace.ref_id)

    def save_workspace(self, notion_workspace: NotionWorkspace) -> NotionWorkspace:
        """Change the root Notion structure."""
        try:
            self._pages_manager.save_page(NotionLockKey(self._KEY), notion_workspace.name)
        except NotionPageNotFoundError as err:
            raise NotionWorkspaceNotFoundError(f"Cannot find Notion workspace") from err
        return notion_workspace

    def load_workspace(self, ref_id: EntityId) -> NotionWorkspace:
        """Retrieve the workspace from Notion side."""
        try:
            workspace_page = self._pages_manager.get_page_extra(NotionLockKey(self._KEY))
        except NotionPageNotFoundError as err:
            raise NotionWorkspaceNotFoundError(f"Cannot find Notion workspace") from err
        return NotionWorkspace(
            name=workspace_page.name,
            notion_id=workspace_page.notion_id,
            ref_id=ref_id)

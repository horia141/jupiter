"""The service class for dealing with workspaces."""
import logging
from typing import Final, Optional

from domain.common.entity_name import EntityName
from domain.common.timezone import Timezone
from domain.common.sync_prefer import SyncPrefer
from models.framework import EntityId
from remote.notion.common import NotionPageLink
from remote.notion.workspaces_manager import WorkspaceSingleton
from repository.workspace import WorkspaceRepository, Workspace

LOGGER = logging.getLogger(__name__)


class WorkspacesService:
    """The service class for dealing with services."""

    _repository: Final[WorkspaceRepository]
    _singleton: Final[WorkspaceSingleton]

    def __init__(
            self, repository: WorkspaceRepository, singleton: WorkspaceSingleton) -> None:
        """Constructor."""
        self._repository = repository
        self._singleton = singleton

    def create_workspace(self, name: EntityName, timezone: Timezone) -> NotionPageLink:
        """Create a workspace."""
        self._repository.create_workspace(name, timezone, None)
        LOGGER.info("Applied local changes")

        new_workspace_page = self._singleton.upsert_notion_structure(name)
        LOGGER.info("Apply Notion changes")

        return new_workspace_page

    def get_workspace_notion_structure(self) -> NotionPageLink:
        """Return a link to the Notion-side structure, maybe like a hack."""
        return self._singleton.get_notion_structure()

    def set_workspace_name(self, name: EntityName) -> Workspace:
        """Set the name of the workspace."""
        workspace = self._repository.load_workspace()
        workspace.name = name
        self._repository.save_workspace(workspace)

        workspace_screen = self._singleton.load_workspace_screen()
        workspace_screen.name = str(name)
        self._singleton.save_workspace_screen(workspace_screen)

        return workspace

    def set_workspace_timezone(self, timezone: Timezone) -> Workspace:
        """Set the timezone of the workspace."""
        workspace = self._repository.load_workspace()
        workspace.timezone = timezone
        self._repository.save_workspace(workspace)

        return workspace

    def set_workspace_default_project_ref_id(self, default_project_ref_id: Optional[EntityId]) -> Workspace:
        """Set the timezone of the workspace."""
        workspace = self._repository.load_workspace()
        workspace.default_project_ref_id = default_project_ref_id
        self._repository.save_workspace(workspace)

        return workspace

    def load_workspace(self) -> Workspace:
        """Retrieve the workspace."""
        workspace = self._repository.load_workspace()
        return workspace

    def workspace_sync(self, sync_prefer: SyncPrefer) -> None:
        """Synchronise workspaces between Notion and the local one."""
        workspace = self._repository.load_workspace()
        workspace_screen = self._singleton.load_workspace_screen()

        if sync_prefer == SyncPrefer.NOTION:
            workspace.name = EntityName.from_raw(workspace_screen.name)
            self._repository.save_workspace(workspace)
            LOGGER.info("Applied changes on local side")
        elif sync_prefer == SyncPrefer.LOCAL:
            workspace_screen.name = str(workspace.name)
            self._singleton.save_workspace_screen(workspace_screen)
            LOGGER.info("Applied changes on Notion side")
        else:
            raise Exception(f"Invalid preference {sync_prefer}")

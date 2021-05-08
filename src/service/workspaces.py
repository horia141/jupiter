"""The service class for dealing with workspaces."""
import logging
from typing import Final, Optional

from pendulum.tz.timezone import Timezone

from models.basic import BasicValidator, SyncPrefer, EntityId
from models.errors import ModelValidationError
from remote.notion.common import NotionPageLink
from remote.notion.workspaces import WorkspaceSingleton
from repository.workspace import WorkspaceRepository, Workspace
from service.errors import ServiceValidationError

LOGGER = logging.getLogger(__name__)


class WorkspacesService:
    """The service class for dealing with services."""

    _basic_validator: Final[BasicValidator]
    _repository: Final[WorkspaceRepository]
    _singleton: Final[WorkspaceSingleton]

    def __init__(
            self, basic_validator: BasicValidator, repository: WorkspaceRepository,
            singleton: WorkspaceSingleton) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._repository = repository
        self._singleton = singleton

    def create_workspace(self, name: str, timezone: Timezone) -> NotionPageLink:
        """Create a workspace."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        self._repository.create_workspace(name, timezone, None)
        LOGGER.info("Applied local changes")

        new_workspace_page = self._singleton.upsert_notion_structure(name)
        LOGGER.info("Apply Notion changes")

        return new_workspace_page

    def get_workspace_notion_structure(self) -> NotionPageLink:
        """Return a link to the Notion-side structure, maybe like a hack."""
        return self._singleton.get_notion_structure()

    def set_workspace_name(self, name: str) -> Workspace:
        """Set the name of the workspace."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        workspace = self._repository.load_workspace()
        workspace.name = name
        self._repository.save_workspace(workspace)

        workspace_screen = self._singleton.load_workspace_screen()
        workspace_screen.name = name
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
            workspace.name = workspace_screen.name
            self._repository.save_workspace(workspace)
            LOGGER.info("Applied changes on local side")
        elif sync_prefer == SyncPrefer.LOCAL:
            workspace_screen.name = workspace.name
            self._singleton.save_workspace_screen(workspace_screen)
            LOGGER.info("Applied changes on Notion side")
        else:
            raise Exception(f"Invalid preference {sync_prefer}")

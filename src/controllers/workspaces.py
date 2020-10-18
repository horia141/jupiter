"""The controller for workspaces."""
import logging
from typing import Final

from pendulum.tz.timezone import Timezone

from models.basic import WorkspaceSpaceId, WorkspaceToken
from remote.notion.infra.connection import NotionConnection
from repository.workspace import Workspace
from service.smart_lists import SmartListsService
from service.vacations import VacationsService
from service.workspaces import WorkspacesService

LOGGER = logging.getLogger(__name__)


class WorkspacesController:
    """The controller for workspaces."""

    _notion_connection: Final[NotionConnection]
    _workspaces_service: Final[WorkspacesService]
    _vacations_service: Final[VacationsService]
    _smart_lists_service: Final[SmartListsService]

    def __init__(
            self, notion_connection: NotionConnection, workspaces_service: WorkspacesService,
            vacations_service: VacationsService, smart_lists_service: SmartListsService) -> None:
        """Constructor."""
        self._notion_connection = notion_connection
        self._workspaces_service = workspaces_service
        self._vacations_service = vacations_service
        self._smart_lists_service = smart_lists_service

    def create_workspace(
            self, name: str, timezone: Timezone, space_id: WorkspaceSpaceId, token: WorkspaceToken) -> None:
        """Create a workspace."""
        self._notion_connection.initialize(space_id, token)
        LOGGER.info("Initialised Notion connection")

        LOGGER.info("Creating workspace")
        new_workspace_page = self._workspaces_service.create_workspace(name, timezone)
        LOGGER.info("Creating vacations")
        self._vacations_service.upsert_root_notion_structure(new_workspace_page)
        LOGGER.info("Creating lists")
        self._smart_lists_service.upsert_root_notion_structure(new_workspace_page)

    def set_workspace_name(self, name: str) -> Workspace:
        """Change the workspace name."""
        return self._workspaces_service.set_workspace_name(name)

    def set_workspace_timezone(self, timezone: Timezone) -> Workspace:
        """Change the workspace timezone."""
        return self._workspaces_service.set_workspace_timezone(timezone)

    def set_workspace_token(self, token: WorkspaceToken) -> None:
        """Change the workspace token."""
        self._notion_connection.update_token(token)

    def load_workspace(self) -> Workspace:
        """Retrieve a workspace."""
        return self._workspaces_service.load_workspace()

"""The controller for workspaces."""
import logging
from dataclasses import dataclass
from typing import Final, Optional

from pendulum.tz.timezone import Timezone

from models.basic import WorkspaceSpaceId, WorkspaceToken, ProjectKey
from remote.notion.infra.connection import NotionConnection
from repository.workspace import Workspace
from service.metrics import MetricsService
from service.projects import ProjectsService, Project
from service.smart_lists import SmartListsService
from service.vacations import VacationsService
from service.workspaces import WorkspacesService

LOGGER = logging.getLogger(__name__)


@dataclass()
class _LoadWorkspaceResponse:

    workspace: Workspace
    default_project: Optional[Project]


class WorkspacesController:
    """The controller for workspaces."""

    _notion_connection: Final[NotionConnection]
    _workspaces_service: Final[WorkspacesService]
    _vacations_service: Final[VacationsService]
    _projects_service: Final[ProjectsService]
    _smart_lists_service: Final[SmartListsService]
    _metrics_service: Final[MetricsService]

    def __init__(
            self, notion_connection: NotionConnection, workspaces_service: WorkspacesService,
            vacations_service: VacationsService, projects_service: ProjectsService,
            smart_lists_service: SmartListsService, metrics_service: MetricsService) -> None:
        """Constructor."""
        self._notion_connection = notion_connection
        self._workspaces_service = workspaces_service
        self._vacations_service = vacations_service
        self._projects_service = projects_service
        self._smart_lists_service = smart_lists_service
        self._metrics_service = metrics_service

    def create_workspace(
            self, name: str, timezone: Timezone, space_id: WorkspaceSpaceId, token: WorkspaceToken) -> None:
        """Create a workspace."""
        self._notion_connection.initialize(space_id, token)
        LOGGER.info("Initialised Notion connection")

        LOGGER.info("Creating workspace")
        new_workspace_page = self._workspaces_service.create_workspace(name, timezone)
        LOGGER.info("Creating vacations")
        self._vacations_service.upsert_root_notion_structure(new_workspace_page)
        LOGGER.info("Creating projects")
        self._projects_service.upsert_root_notion_structure(new_workspace_page)
        LOGGER.info("Creating lists")
        self._smart_lists_service.upsert_root_notion_structure(new_workspace_page)
        LOGGER.info("Creating metrics")
        self._metrics_service.upsert_root_notion_structure(new_workspace_page)

    def set_workspace_name(self, name: str) -> Workspace:
        """Change the workspace name."""
        return self._workspaces_service.set_workspace_name(name)

    def set_workspace_timezone(self, timezone: Timezone) -> Workspace:
        """Change the workspace timezone."""
        return self._workspaces_service.set_workspace_timezone(timezone)

    def set_workspace_default_project(self, project_key: Optional[ProjectKey]) -> Workspace:
        """Change the workspace name."""
        if project_key:
            project = self._projects_service.load_project_by_key(project_key)
            return self._workspaces_service.set_workspace_default_project_ref_id(project.ref_id)
        else:
            return self._workspaces_service.set_workspace_default_project_ref_id(None)

    def set_workspace_token(self, token: WorkspaceToken) -> None:
        """Change the workspace token."""
        self._notion_connection.update_token(token)

    def load_workspace(self) -> _LoadWorkspaceResponse:
        """Retrieve a workspace."""
        workspace = self._workspaces_service.load_workspace()
        default_project = None
        if workspace.default_project_ref_id:
            default_project = self._projects_service.load_project_by_ref_id(workspace.default_project_ref_id)
        return _LoadWorkspaceResponse(workspace, default_project)

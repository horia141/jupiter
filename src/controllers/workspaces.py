"""The controller for workspaces."""
import logging
from dataclasses import dataclass
from typing import Final, Optional

from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.prm_database import PrmDatabase
from domain.workspaces.notion_token import NotionToken
from domain.workspaces.notion_space_id import NotionSpaceId
from domain.common.entity_name import EntityName
from domain.projects.project_key import ProjectKey
from domain.common.timezone import Timezone
from remote.notion.infra.connection import NotionConnection
from repository.workspace import Workspace
from service.metrics import MetricsService
from service.projects import ProjectsService, Project
from service.smart_lists import SmartListsService
from service.vacations import VacationsService
from service.workspaces import WorkspacesService
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class _LoadWorkspaceResponse:

    workspace: Workspace
    default_project: Optional[Project]


class WorkspacesController:
    """The controller for workspaces."""

    _time_provider: Final[TimeProvider]
    _notion_connection: Final[NotionConnection]
    _workspaces_service: Final[WorkspacesService]
    _vacations_service: Final[VacationsService]
    _projects_service: Final[ProjectsService]
    _smart_lists_service: Final[SmartListsService]
    _metrics_service: Final[MetricsService]
    _prm_engine: Final[PrmEngine]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self, time_provider: TimeProvider, notion_connection: NotionConnection,
            workspaces_service: WorkspacesService, vacations_service: VacationsService,
            projects_service: ProjectsService, smart_lists_service: SmartListsService, metrics_service: MetricsService,
            prm_engine: PrmEngine, prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._notion_connection = notion_connection
        self._workspaces_service = workspaces_service
        self._vacations_service = vacations_service
        self._projects_service = projects_service
        self._smart_lists_service = smart_lists_service
        self._metrics_service = metrics_service
        self._prm_engine = prm_engine
        self._prm_notion_manager = prm_notion_manager

    def create_workspace(
            self, name: EntityName, timezone: Timezone, notion_space_id: NotionSpaceId, notion_token: NotionToken,
            first_project_key: ProjectKey, first_project_name: EntityName) -> None:
        """Create a workspace."""
        self._notion_connection.initialize(notion_space_id, notion_token)
        LOGGER.info("Initialised Notion connection")

        LOGGER.info("Creating workspace")
        new_workspace_page = self._workspaces_service.create_workspace(name, timezone)
        LOGGER.info("Creating vacations")
        self._vacations_service.upsert_root_notion_structure(new_workspace_page)
        LOGGER.info("Creating projects")
        self._projects_service.upsert_root_notion_structure(new_workspace_page)
        default_project = self._projects_service.create_project(first_project_key, first_project_name)
        self._workspaces_service.set_workspace_default_project_ref_id(default_project.ref_id)
        LOGGER.info("Creating lists")
        self._smart_lists_service.upsert_root_notion_structure(new_workspace_page)
        LOGGER.info("Creating metrics")
        self._metrics_service.upsert_root_notion_structure(new_workspace_page)
        LOGGER.info("Creating the PRM database")
        with self._prm_engine.get_unit_of_work() as uow:
            prm_database = PrmDatabase.new_prm_database(default_project.ref_id, self._time_provider.get_current_time())
            uow.prm_database_repository.create(prm_database)
        self._prm_notion_manager.upsert_root_notion_structure(new_workspace_page)

    def set_workspace_name(self, name: EntityName) -> Workspace:
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

    def set_workspace_notion_token(self, notion_token: NotionToken) -> None:
        """Change the workspace token."""
        self._notion_connection.update_token(notion_token)

    def load_workspace(self) -> _LoadWorkspaceResponse:
        """Retrieve a workspace."""
        workspace = self._workspaces_service.load_workspace()
        default_project = None
        if workspace.default_project_ref_id:
            default_project = self._projects_service.load_project_by_ref_id(workspace.default_project_ref_id)
        return _LoadWorkspaceResponse(workspace, default_project)

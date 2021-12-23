"""UseCase for initialising the workspace."""
import logging
from dataclasses import dataclass
from typing import Final

from domain.entity_name import EntityName
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.prm_database import PrmDatabase
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.infra.project_notion_manager import ProjectNotionManager
from domain.projects.project import Project
from domain.projects.project_key import ProjectKey
from domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from domain.timezone import Timezone
from domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from domain.workspaces.infra.workspace_engine import WorkspaceEngine
from domain.workspaces.infra.workspace_notion_manager import WorkspaceNotionManager
from domain.workspaces.notion_space_id import NotionSpaceId
from domain.workspaces.notion_token import NotionToken
from domain.workspaces.workspace import Workspace
from framework.base.entity_id import BAD_REF_ID
from framework.use_case import UseCase
from remote.notion.infra.connection import NotionConnection
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InitUseCase(UseCase['InitUseCase.Args', None]):
    """UseCase for initialising the workspace."""

    @dataclass()
    class Args:
        """Args."""
        name: EntityName
        timezone: Timezone
        notion_space_id: NotionSpaceId
        notion_token: NotionToken
        first_project_key: ProjectKey
        first_project_name: EntityName

    _time_provider: Final[TimeProvider]
    _notion_connection: Final[NotionConnection]
    _workspace_engine: Final[WorkspaceEngine]
    _workspace_notion_manager: Final[WorkspaceNotionManager]
    _vacation_notion_manager: Final[VacationNotionManager]
    _project_engine: Final[ProjectEngine]
    _project_notion_manager: Final[ProjectNotionManager]
    _smart_list_notion_manager: Final[SmartListNotionManager]
    _metric_notion_manager: Final[MetricNotionManager]
    _prm_engine: Final[PrmEngine]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self, time_provider: TimeProvider, notion_connection: NotionConnection,
            workspace_engine: WorkspaceEngine, workspace_notion_manager: WorkspaceNotionManager,
            vacation_notion_manager: VacationNotionManager,
            project_engine: ProjectEngine, project_notion_manager: ProjectNotionManager,
            smart_list_notion_manager: SmartListNotionManager, metric_notion_manager: MetricNotionManager,
            prm_engine: PrmEngine, prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._notion_connection = notion_connection
        self._workspace_engine = workspace_engine
        self._workspace_notion_manager = workspace_notion_manager
        self._vacation_notion_manager = vacation_notion_manager
        self._project_engine = project_engine
        self._project_notion_manager = project_notion_manager
        self._metric_notion_manager = metric_notion_manager
        self._smart_list_notion_manager = smart_list_notion_manager
        self._prm_engine = prm_engine
        self._prm_notion_manager = prm_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        self._notion_connection.initialize(args.notion_space_id, args.notion_token)
        LOGGER.info("Initialised Notion connection")

        LOGGER.info("Creating workspace")
        with self._workspace_engine.get_unit_of_work() as workspace_uow:
            new_workspace = \
                Workspace.new_workspace(args.name, args.timezone, BAD_REF_ID, self._time_provider.get_current_time())
            new_workspace = workspace_uow.workspace_repository.create(new_workspace)
        LOGGER.info("Applied local changes")

        new_notion_workspace = self._workspace_notion_manager.upsert_workspace(new_workspace)
        LOGGER.info("Apply Notion changes")

        LOGGER.info("Creating vacations")
        self._vacation_notion_manager.upsert_root_page(new_notion_workspace)
        LOGGER.info("Creating projects")
        self._project_notion_manager.upsert_root_page(new_notion_workspace)
        with self._project_engine.get_unit_of_work() as project_uow:
            new_default_project = \
                Project.new_project(
                    args.first_project_key, args.first_project_name, self._time_provider.get_current_time())
            new_default_project = project_uow.project_repository.create(new_default_project)
            LOGGER.info("Created first project")
        self._project_notion_manager.upsert_project(new_default_project)
        LOGGER.info("Created first project on Notion side")
        with self._workspace_engine.get_unit_of_work() as workspace_uow_two:
            new_workspace.change_default_project(new_default_project.ref_id, self._time_provider.get_current_time())
            workspace_uow_two.workspace_repository.save(new_workspace)
        LOGGER.info("Creating lists")
        self._smart_list_notion_manager.upsert_root_page(new_notion_workspace)
        LOGGER.info("Creating metrics")
        self._metric_notion_manager.upsert_root_page(new_notion_workspace)
        LOGGER.info("Creating the PRM database")
        with self._prm_engine.get_unit_of_work() as prm_uow:
            prm_database = \
                PrmDatabase.new_prm_database(new_default_project.ref_id, self._time_provider.get_current_time())
            prm_uow.prm_database_repository.create(prm_database)
        self._prm_notion_manager.upsert_root_notion_structure(new_notion_workspace)

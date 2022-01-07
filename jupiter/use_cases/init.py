"""UseCase for initialising the workspace."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.prm.infra.prm_notion_manager import PrmNotionManager
from jupiter.domain.prm.prm_database import PrmDatabase
from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager
from jupiter.domain.projects.notion_project import NotionProject
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.projects.project_name import ProjectName
from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from jupiter.domain.storage_engine import StorageEngine
from jupiter.domain.timezone import Timezone
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from jupiter.domain.workspaces.infra.workspace_notion_manager import WorkspaceNotionManager
from jupiter.domain.workspaces.notion_space_id import NotionSpaceId
from jupiter.domain.workspaces.notion_token import NotionToken
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.domain.workspaces.workspace_name import WorkspaceName
from jupiter.framework.base.entity_id import BAD_REF_ID
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCase
from jupiter.remote.notion.infra.connection import NotionConnection
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class InitUseCase(UseCase['InitUseCase.Args', None]):
    """UseCase for initialising the workspace."""

    @dataclass()
    class Args:
        """Args."""
        name: WorkspaceName
        timezone: Timezone
        notion_space_id: NotionSpaceId
        notion_token: NotionToken
        first_project_key: ProjectKey
        first_project_name: ProjectName

    _time_provider: Final[TimeProvider]
    _notion_connection: Final[NotionConnection]
    _storage_engine: Final[StorageEngine]
    _workspace_notion_manager: Final[WorkspaceNotionManager]
    _vacation_notion_manager: Final[VacationNotionManager]
    _project_notion_manager: Final[ProjectNotionManager]
    _smart_list_notion_manager: Final[SmartListNotionManager]
    _metric_notion_manager: Final[MetricNotionManager]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self, time_provider: TimeProvider, notion_connection: NotionConnection,
            storage_engine: StorageEngine, workspace_notion_manager: WorkspaceNotionManager,
            vacation_notion_manager: VacationNotionManager, project_notion_manager: ProjectNotionManager,
            smart_list_notion_manager: SmartListNotionManager, metric_notion_manager: MetricNotionManager,
            prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._notion_connection = notion_connection
        self._storage_engine = storage_engine
        self._workspace_notion_manager = workspace_notion_manager
        self._vacation_notion_manager = vacation_notion_manager
        self._project_notion_manager = project_notion_manager
        self._metric_notion_manager = metric_notion_manager
        self._smart_list_notion_manager = smart_list_notion_manager
        self._prm_notion_manager = prm_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        self._notion_connection.initialize(args.notion_space_id, args.notion_token)
        LOGGER.info("Initialised Notion connection")

        LOGGER.info("Creating workspace")
        with self._storage_engine.get_unit_of_work() as uow:
            new_workspace = \
                Workspace.new_workspace(
                    name=args.name, timezone=args.timezone, default_project_ref_id=BAD_REF_ID,
                    source=EventSource.CLI, created_time=self._time_provider.get_current_time())
            new_workspace = uow.workspace_repository.create(new_workspace)

            new_default_project = \
                Project.new_project(
                    key=args.first_project_key, name=args.first_project_name, source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            new_default_project = uow.project_repository.create(new_default_project)

            LOGGER.info("Created first project")
            new_workspace.change_default_project(
                default_project_ref_id=new_default_project.ref_id, source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time())
            uow.workspace_repository.save(new_workspace)
            prm_database = \
                PrmDatabase.new_prm_database(
                    catch_up_project_ref_id=new_default_project.ref_id, source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            uow.prm_database_repository.create(prm_database)
            LOGGER.info("Creating the PRM database")

        LOGGER.info("Applied local changes")

        new_notion_workspace = NotionWorkspace.new_notion_row(new_workspace)
        new_notion_workspace = self._workspace_notion_manager.upsert_workspace(new_notion_workspace)

        self._vacation_notion_manager.upsert_root_page(new_notion_workspace)
        self._project_notion_manager.upsert_root_page(new_notion_workspace)
        new_notion_default_project = NotionProject.new_notion_row(new_default_project)
        self._project_notion_manager.upsert_project(new_notion_default_project)
        self._smart_list_notion_manager.upsert_root_page(new_notion_workspace)
        self._metric_notion_manager.upsert_root_page(new_notion_workspace)
        self._prm_notion_manager.upsert_root_notion_structure(new_notion_workspace)

        LOGGER.info("Applied Notion changes")

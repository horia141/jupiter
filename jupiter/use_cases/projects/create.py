"""The command for creating a project."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager
from jupiter.domain.projects.notion_project import NotionProject
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.projects.project_name import ProjectName
from jupiter.domain.projects.service.project_label_update_service import ProjectLabelUpdateService
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class ProjectCreateUseCase(AppMutationUseCase['ProjectCreateUseCase.Args', None]):
    """The command for creating a project."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        key: ProjectKey
        name: ProjectName

    _project_notion_manager: Final[ProjectNotionManager]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            project_notion_manager: ProjectNotionManager,
            inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_notion_manager: RecurringTaskNotionManager,
            big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._project_notion_manager = project_notion_manager
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_notion_manager = recurring_task_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_workspace(workspace.ref_id)

            new_project = \
                Project.new_project(
                    project_collection_ref_id=project_collection.ref_id, key=args.key, name=args.name,
                    source=EventSource.CLI, created_time=self._time_provider.get_current_time())

            new_project = uow.project_repository.create(new_project)
        LOGGER.info("Applied local changes")

        new_notion_project = NotionProject.new_notion_row(new_project, NotionProject.DirectInfo())
        self._project_notion_manager.upsert_project(project_collection.ref_id, new_notion_project)
        LOGGER.info("Applied Notion changes")

        with self._storage_engine.get_unit_of_work() as uow:
            projects = uow.project_repository.find_all(project_collection.ref_id)

        ProjectLabelUpdateService(
            self._storage_engine,
            self._inbox_task_notion_manager,
            self._recurring_task_notion_manager,
            self._big_plan_notion_manager)\
            .sync(workspace, projects)

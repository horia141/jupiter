"""The command for updating a project."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.chores.infra.chore_notion_manager import ChoreNotionManager
from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager
from jupiter.domain.projects.notion_project import NotionProject
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.projects.project_name import ProjectName
from jupiter.domain.projects.service.project_label_update_service import ProjectLabelUpdateService
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class ProjectUpdateUseCase(AppMutationUseCase['ProjectUpdateUseCase.Args', None]):
    """The command for updating a project."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        key: ProjectKey
        name: UpdateAction[ProjectName]

    _project_notion_manager: Final[ProjectNotionManager]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _habit_notion_manager: Final[HabitNotionManager]
    _chore_notion_manager: Final[ChoreNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            project_notion_manager: ProjectNotionManager,
            inbox_task_notion_manager: InboxTaskNotionManager,
            habit_notion_manager: HabitNotionManager,
            chore_notion_manager: ChoreNotionManager,
            big_plan_notion_manager: BigPlanNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._project_notion_manager = project_notion_manager
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._habit_notion_manager = habit_notion_manager
        self._chore_notion_manager = chore_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            project_collection = uow.project_collection_repository.load_by_workspace(workspace.ref_id)
            project = uow.project_repository.load_by_key(project_collection.ref_id, args.key)
            project = project.update(
                name=args.name, source=EventSource.CLI, modification_time=self._time_provider.get_current_time())
            uow.project_repository.save(project)
        LOGGER.info("Applied local changes")

        notion_project = self._project_notion_manager.load_project(project_collection.ref_id, project.ref_id)
        notion_project = notion_project.join_with_entity(project, NotionProject.DirectInfo())
        self._project_notion_manager.save_project(project_collection.ref_id, notion_project)
        LOGGER.info("Applied Notion changes")

        with self._storage_engine.get_unit_of_work() as uow:
            projects = uow.project_repository.find_all(project_collection.ref_id)

        ProjectLabelUpdateService(
            self._storage_engine,
            self._inbox_task_notion_manager,
            self._habit_notion_manager,
            self._chore_notion_manager,
            self._big_plan_notion_manager)\
            .sync(workspace, projects)

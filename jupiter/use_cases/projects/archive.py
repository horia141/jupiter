"""The command for archiving a project."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.errors import InputValidationError
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class ProjectArchiveUseCase(AppMutationUseCase['ProjectArchiveUseCase.Args', None]):
    """The command for archiving a project."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        key: ProjectKey

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
        with self._storage_engine.get_unit_of_work() as uow:
            project = uow.project_repository.load_by_key(args.key)
            workspace = uow.workspace_repository.load()

            if workspace.default_project_ref_id == project.ref_id:
                raise InputValidationError("Cannot archive project because it is the default workspace one")

            metrics = uow.metric_repository.find_all(allow_archived=True)
            for metric in metrics:
                if metric.collection_params is not None and metric.collection_params.project_ref_id == project.ref_id:
                    raise InputValidationError(
                        "Cannot archive project because it is the collection project " +
                        f"for metric '{metric.name} archived={metric.archived}'")

            prm_database = uow.prm_database_repository.load()
            if prm_database.catch_up_project_ref_id == project.ref_id:
                raise InputValidationError(
                    "Cannot archive project because it is the collection project for the PRM database")

            inbox_task_collection = uow.inbox_task_collection_repository.load_by_project(project.ref_id)

            inbox_tasks = \
                uow.inbox_task_repository.find_all(filter_inbox_task_collection_ref_ids=[inbox_task_collection.ref_id])

            for inbox_task in inbox_tasks:
                inbox_task = inbox_task.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
                uow.inbox_task_repository.save(inbox_task)

            inbox_task_collection = \
                inbox_task_collection.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
            uow.inbox_task_collection_repository.save(inbox_task_collection)

            big_plan_collection = uow.big_plan_collection_repository.load_by_project(project.ref_id)
            big_plans = \
                uow.big_plan_repository.find_all(filter_big_plan_collection_ref_ids=[big_plan_collection.ref_id])

            for big_plan in big_plans:
                big_plan = big_plan.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
                uow.big_plan_repository.save(big_plan)

            big_plan_collection = \
                big_plan_collection.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
            uow.big_plan_collection_repository.save(big_plan_collection)

            recurring_task_collection = uow.recurring_task_collection_repository.load_by_project(project.ref_id)
            recurring_tasks = \
                uow.recurring_task_repository.find_all(
                    filter_recurring_task_collection_ref_ids=[recurring_task_collection.ref_id])

            for recurring_task in recurring_tasks:
                recurring_task = recurring_task.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
                uow.recurring_task_repository.save(recurring_task)

            recurring_task_collection =\
                recurring_task_collection.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
            uow.recurring_task_collection_repository.save(recurring_task_collection)

            project = project.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
            uow.project_repository.save(project)
        LOGGER.info("Applied local changes")

        self._inbox_task_notion_manager.remove_inbox_tasks_collection(inbox_task_collection.ref_id)
        self._big_plan_notion_manager.remove_big_plans_collection(big_plan_collection.ref_id)
        self._recurring_task_notion_manager.remove_recurring_tasks_collection(recurring_task_collection.ref_id)
        self._project_notion_manager.remove_project(project.ref_id)
        LOGGER.info("Applied Notion changes")

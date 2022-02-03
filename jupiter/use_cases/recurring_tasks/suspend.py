"""The command for suspend a recurring task."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from jupiter.domain.recurring_tasks.notion_recurring_task import NotionRecurringTask
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider


class RecurringTaskSuspendUseCase(AppMutationUseCase['RecurringTaskSuspendUseCase.Args', None]):
    """The command for suspending a recurring task."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId

    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            recurring_task = uow.recurring_task_repository.load_by_id(args.ref_id)
            project = uow.project_repository.load_by_id(recurring_task.project_ref_id)
            recurring_task = \
                recurring_task.suspend(source=EventSource.CLI, modification_time=self._time_provider.get_current_time())
            uow.recurring_task_repository.save(recurring_task)

        direct_info = NotionRecurringTask.DirectInfo(project_name=project.name)
        notion_recurring_task = self._recurring_task_notion_manager.load_recurring_task(
            recurring_task.recurring_task_collection_ref_id, recurring_task.ref_id)
        notion_recurring_task = notion_recurring_task.join_with_aggregate_root(recurring_task, direct_info)
        self._recurring_task_notion_manager.save_recurring_task(
            recurring_task.recurring_task_collection_ref_id, notion_recurring_task)

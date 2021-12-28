"""The command for suspend a recurring task."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.recurring_tasks.infra.recurring_task_engine import RecurringTaskEngine
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class RecurringTaskSuspendUseCase(UseCase['RecurringTaskSuspendUseCase.Args', None]):
    """The command for suspending a recurring task."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        suspended: bool

    _time_provider: Final[TimeProvider]
    _recurring_task_engine: Final[RecurringTaskEngine]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, recurring_task_engine: RecurringTaskEngine,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._recurring_task_engine = recurring_task_engine
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._recurring_task_engine.get_unit_of_work() as uow:
            recurring_task = uow.recurring_task_repository.load_by_id(args.ref_id)
            recurring_task.change_suspended(args.suspended, self._time_provider.get_current_time())
            uow.recurring_task_repository.save(recurring_task)

        notion_recurring_task = self._recurring_task_notion_manager.load_recurring_task(
            recurring_task.recurring_task_collection_ref_id, recurring_task.ref_id)
        notion_recurring_task = notion_recurring_task.join_with_aggregate_root(recurring_task, None)
        self._recurring_task_notion_manager.save_recurring_task(
            recurring_task.recurring_task_collection_ref_id, notion_recurring_task)

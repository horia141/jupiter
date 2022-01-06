"""The command for unsuspending a recurring task."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class RecurringTaskUnsuspendUseCase(UseCase['RecurringTaskUnsuspendUseCase.Args', None]):
    """The command for unsuspending a recurring task."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: StorageEngine,
            recurring_task_notion_manager: RecurringTaskNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._recurring_task_notion_manager = recurring_task_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            recurring_task = uow.recurring_task_repository.load_by_id(args.ref_id)
            recurring_task.unsuspend(self._time_provider.get_current_time())
            uow.recurring_task_repository.save(recurring_task)

        notion_recurring_task = self._recurring_task_notion_manager.load_recurring_task(
            recurring_task.recurring_task_collection_ref_id, recurring_task.ref_id)
        notion_recurring_task = notion_recurring_task.join_with_aggregate_root(recurring_task, None)
        self._recurring_task_notion_manager.save_recurring_task(
            recurring_task.recurring_task_collection_ref_id, notion_recurring_task)

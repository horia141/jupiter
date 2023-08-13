"""Shared service for removing a habit."""
from typing import Final

from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import ProgressReporter


class HabitRemoveService:
    """Shared service for removing a habit."""

    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    async def remove(
        self,
        progress_reporter: ProgressReporter,
        ref_id: EntityId,
    ) -> None:
        """Hard remove a habit."""
        async with self._storage_engine.get_unit_of_work() as uow:
            habit = await uow.habit_repository.load_by_id(ref_id, allow_archived=True)
            habit_collection = await uow.habit_collection_repository.load_by_id(
                habit.habit_collection_ref_id,
            )
            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    habit_collection.workspace_ref_id,
                )
            )
            inbox_tasks_to_archive = (
                await uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_habit_ref_ids=[habit.ref_id],
                )
            )

            for inbox_task in inbox_tasks_to_archive:
                await uow.inbox_task_repository.remove(inbox_task.ref_id)
                await progress_reporter.mark_removed(inbox_task)

            await uow.habit_repository.remove(ref_id)
            await progress_reporter.mark_removed(habit)

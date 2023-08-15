"""Shared service for archiving a habit."""
from typing import Final

from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


class HabitArchiveService:
    """Shared service for archiving a habit."""

    _source: Final[EventSource]
    _time_provider: Final[TimeProvider]

    def __init__(
        self,
        source: EventSource,
        time_provider: TimeProvider,
    ) -> None:
        """Constructor."""
        self._source = source
        self._time_provider = time_provider

    async def do_it(
        self, uow: DomainUnitOfWork, progress_reporter: ProgressReporter, habit: Habit
    ) -> None:
        """Execute the service's action."""
        if habit.archived:
            return

        habit_collection = await uow.habit_collection_repository.load_by_id(
            habit.habit_collection_ref_id,
        )
        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                habit_collection.workspace_ref_id,
            )
        )
        inbox_tasks_to_archive = await uow.inbox_task_repository.find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=False,
            filter_habit_ref_ids=[habit.ref_id],
        )

        for inbox_task in inbox_tasks_to_archive:
            inbox_task = inbox_task.mark_archived(
                self._source,
                self._time_provider.get_current_time(),
            )
            await uow.inbox_task_repository.save(inbox_task)
            await progress_reporter.mark_updated(inbox_task)

        habit = habit.mark_archived(
            self._source,
            self._time_provider.get_current_time(),
        )
        await uow.habit_repository.save(habit)
        await progress_reporter.mark_updated(habit)

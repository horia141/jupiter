"""Shared service for archiving a habit."""

from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter


class HabitArchiveService:
    """Shared service for archiving a habit."""

    async def do_it(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        habit: Habit,
    ) -> None:
        """Execute the service's action."""
        if habit.archived:
            return

        habit_collection = await uow.habit_collection_repository.load_by_id(
            habit.habit_collection.ref_id,
        )
        inbox_task_collection = (
            await uow.inbox_task_collection_repository.load_by_parent(
                habit_collection.workspace.ref_id,
            )
        )
        inbox_tasks_to_archive = await uow.inbox_task_repository.find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=False,
            filter_habit_ref_ids=[habit.ref_id],
        )

        inbox_task_archive_service = InboxTaskArchiveService()

        for inbox_task in inbox_tasks_to_archive:
            await inbox_task_archive_service.do_it(
                ctx, uow, progress_reporter, inbox_task
            )

        habit = habit.mark_archived(ctx)
        await uow.habit_repository.save(habit)
        await progress_reporter.mark_updated(habit)

"""Shared service for removing a habit."""

from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter


class HabitRemoveService:
    """Shared service for removing a habit."""

    async def remove(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        ref_id: EntityId,
    ) -> None:
        """Hard remove a habit."""
        habit = await uow.get_for(Habit).load_by_id(ref_id, allow_archived=True)
        habit_collection = await uow.get_for(HabitCollection).load_by_id(
            habit.habit_collection.ref_id,
        )
        inbox_task_collection = await uow.get_for(
            InboxTaskCollection
        ).load_by_parent(
            habit_collection.workspace.ref_id,
        )
        inbox_tasks_to_archive = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            habit_ref_id=[habit.ref_id],
        )

        inbox_task_remove_service = InboxTaskArchiveService()

        for inbox_task in inbox_tasks_to_archive:
            await inbox_task_remove_service.do_it(
                ctx, uow, progress_reporter, inbox_task
            )

        await uow.get_for(Habit).remove(ref_id)
        await progress_reporter.mark_removed(habit)

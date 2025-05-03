"""Shared service for archiving a habit."""

from jupiter.core.domain.application.home.home_config import HomeConfig
from jupiter.core.domain.concept.habits.habit import Habit
from jupiter.core.domain.concept.habits.habit_collection import HabitCollection
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTaskRepository
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.core.archival_reason import ArchivalReason
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_archive_service import (
    NoteArchiveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter


class HabitArchiveService:
    """Shared service for archiving a habit."""

    async def do_it(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        habit: Habit,
        archival_reason: ArchivalReason,
    ) -> None:
        """Execute the service's action."""
        if habit.archived:
            return

        habit_collection = await uow.get_for(HabitCollection).load_by_id(
            habit.habit_collection.ref_id,
        )

        home_config = await uow.get_for(HomeConfig).load_by_parent(
            habit_collection.workspace.ref_id,
        )
        if habit.ref_id in home_config.key_habits:
            home_config = home_config.update(
                ctx=ctx,
                key_habits=UpdateAction.change_to(
                    [
                        habit_ref_id
                        for habit_ref_id in home_config.key_habits
                        if habit_ref_id != habit.ref_id
                    ]
                ),
                key_metrics=UpdateAction.change_to([]),
            )
            await uow.get_for(HomeConfig).save(home_config)

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            habit_collection.workspace.ref_id,
        )
        inbox_tasks_to_archive = await uow.get(
            InboxTaskRepository
        ).find_all_for_source_created_desc(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=False,
            source=InboxTaskSource.HABIT,
            source_entity_ref_id=habit.ref_id,
        )

        inbox_task_archive_service = InboxTaskArchiveService()

        for inbox_task in inbox_tasks_to_archive:
            await inbox_task_archive_service.do_it(
                ctx, uow, progress_reporter, inbox_task, archival_reason
            )

        habit = habit.mark_archived(ctx, archival_reason)
        await uow.get_for(Habit).save(habit)
        await progress_reporter.mark_updated(habit)

        note_archive_service = NoteArchiveService()
        await note_archive_service.archive_for_source(
            ctx, uow, NoteDomain.HABIT, habit.ref_id, archival_reason
        )

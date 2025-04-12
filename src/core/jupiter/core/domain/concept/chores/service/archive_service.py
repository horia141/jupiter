"""Shared service for archiving a chore."""

from jupiter.core.domain.concept.chores.chore import Chore
from jupiter.core.domain.concept.chores.chore_collection import ChoreCollection
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
from jupiter.core.framework.use_case import ProgressReporter


class ChoreArchiveService:
    """Shared service for archiving a chore."""

    async def do_it(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        chore: Chore,
        archival_reason: ArchivalReason,
    ) -> None:
        """Execute the service's action."""
        if chore.archived:
            return

        chore_collection = await uow.get_for(ChoreCollection).load_by_id(
            chore.chore_collection.ref_id,
        )
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            chore_collection.workspace.ref_id,
        )
        inbox_tasks_to_archive = await uow.get(
            InboxTaskRepository
        ).find_all_for_source_created_desc(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=False,
            source=InboxTaskSource.CHORE,
            source_entity_ref_id=chore.ref_id,
        )

        inbox_task_archive_service = InboxTaskArchiveService()

        for inbox_task in inbox_tasks_to_archive:
            await inbox_task_archive_service.do_it(
                ctx, uow, progress_reporter, inbox_task, archival_reason
            )

        chore = chore.mark_archived(ctx, archival_reason)
        await uow.get_for(Chore).save(chore)
        await progress_reporter.mark_updated(chore)

        note_archive_service = NoteArchiveService()
        await note_archive_service.archive_for_source(
            ctx, uow, NoteDomain.CHORE, chore.ref_id, archival_reason
        )

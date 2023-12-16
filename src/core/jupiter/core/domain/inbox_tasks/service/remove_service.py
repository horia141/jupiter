"""Shared service for removing an inbox task."""

from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_remove_service import NoteRemoveService
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import ProgressReporter


class InboxTaskRemoveService:
    """Shared service for removing an inbox task."""

    async def do_it(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        inbox_task: InboxTask,
    ) -> None:
        """Execute the service's action."""
        note_remove_service = NoteRemoveService()
        await note_remove_service.remove_for_source(
            uow, NoteDomain.INBOX_TASK, inbox_task.ref_id
        )
        await uow.inbox_task_repository.remove(inbox_task.ref_id)
        await progress_reporter.mark_removed(inbox_task)

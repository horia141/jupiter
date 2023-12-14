"""Shared service for removing an inbox task."""

from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.notes.note_source import NoteSource
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
        note = await uow.note_repository.remove_optional_for_source(
            NoteSource.INBOX_TASK, inbox_task.ref_id
        )
        if note is not None:
            await progress_reporter.mark_removed(note)

        await uow.inbox_task_repository.remove(inbox_task.ref_id)
        await progress_reporter.mark_removed(inbox_task)

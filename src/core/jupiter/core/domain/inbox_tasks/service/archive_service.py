"""Shared service for archiving an inbox task."""
from typing import Final

from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_archive_service import (
    NoteArchiveService,
)
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


class InboxTaskArchiveService:
    """Shared service for archiving an inbox task."""

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
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        inbox_task: InboxTask,
    ) -> None:
        """Execute the service's action."""
        if inbox_task.archived:
            return

        inbox_task = inbox_task.mark_archived(
            self._source,
            self._time_provider.get_current_time(),
        )
        await uow.inbox_task_repository.save(inbox_task)
        await progress_reporter.mark_updated(inbox_task)

        note_archive_service = NoteArchiveService(
            self._source,
            self._time_provider,
        )
        await note_archive_service.archive_for_source(
            uow, NoteDomain.INBOX_TASK, inbox_task.ref_id
        )

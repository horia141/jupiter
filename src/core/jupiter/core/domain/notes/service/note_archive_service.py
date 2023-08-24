"""Archive a note."""
from typing import Final

from jupiter.core.domain.notes.note import Note
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


class NoteArchiveService:
    """A service for removing a note."""

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
        note: Note,
    ) -> None:
        """Execute the command's action."""
        if note.archived:
            return
        
        subnotes = await uow.note_repository.find_all_with_filters(
            parent_ref_id=note.ref_id,
            allow_archived=True,
            filter_parent_note_ref_ids=[note.ref_id],
        )

        for subnote in subnotes:
            await self.do_it(uow, progress_reporter, subnote)

        note = note.mark_archived(self._source, self._time_provider.get_current_time())
        await uow.note_repository.save(note)
        await progress_reporter.mark_updated(note)

"""Archive a note."""
from typing import Final

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
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

    async def archive(
        self,
        uow: DomainUnitOfWork,
        note: Note,
    ) -> None:
        """Execute the command's action."""
        if note.archived:
            return

        if note.can_be_removed_independently:
            raise Exception(f"Note {note.ref_id} cannot be removed independently")

        note = note.mark_archived(self._source, self._time_provider.get_current_time())
        await uow.note_repository.save(note)

    async def archive_for_source(
        self, uow: DomainUnitOfWork, domain: NoteDomain, source_entity_ref_id: EntityId
    ) -> None:
        """Execute the command's action."""
        note = await uow.note_repository.load_optional_for_source(
            domain, source_entity_ref_id, allow_archived=True
        )

        if note is None:
            return

        if note.archived:
            return

        if note.can_be_removed_independently:
            raise Exception(f"Note {note.ref_id} cannot be removed independently")

        note = note.mark_archived(self._source, self._time_provider.get_current_time())
        await uow.note_repository.save(note)

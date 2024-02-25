"""Archive a note."""

from jupiter.core.domain.core.notes.infra.note_repository import NoteRepository
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext


class NoteArchiveService:
    """A service for removing a note."""

    async def archive(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        note: Note,
    ) -> None:
        """Execute the command's action."""
        if note.archived:
            return

        if note.can_be_removed_independently:
            raise Exception(f"Note {note.ref_id} cannot be removed independently")

        note = note.mark_archived(ctx)
        await uow.get_for(Note).save(note)

    async def archive_for_source(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        domain: NoteDomain,
        source_entity_ref_id: EntityId,
    ) -> None:
        """Execute the command's action."""
        note = await uow.get(NoteRepository).load_optional_for_source(
            domain, source_entity_ref_id, allow_archived=True
        )

        if note is None:
            return

        if note.archived:
            return

        if not note.can_be_removed_independently:
            raise Exception(f"Note {note.ref_id} cannot be removed dependently")

        note = note.mark_archived(ctx)
        await uow.get_for(Note).save(note)

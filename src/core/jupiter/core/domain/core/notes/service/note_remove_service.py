"""Remove a note."""
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId


class NoteRemoveService:
    """A service for removing a note."""

    async def remove(
        self,
        uow: DomainUnitOfWork,
        note: Note,
    ) -> None:
        """Execute the command's action."""
        if note.can_be_removed_independently:
            raise Exception(f"Note {note.ref_id} cannot be removed independently")

        await uow.note_repository.remove(note.ref_id)

    async def remove_for_source(
        self,
        uow: DomainUnitOfWork,
        domain: NoteDomain,
        source_entity_ref_id: EntityId,
    ) -> None:
        """Execute the command's action."""
        note = await uow.note_repository.load_optional_for_source(
            domain, source_entity_ref_id
        )
        if note is None:
            return
        if note.can_be_removed_independently:
            raise Exception(f"Note {note.ref_id} cannot be removed independently")
        await uow.note_repository.remove(note.ref_id)

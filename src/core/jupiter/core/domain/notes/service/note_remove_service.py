"""Remove a note."""
from jupiter.core.domain.notes.note import Note
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import ProgressReporter


class NoteRemoveService:
    """A service for removing a note."""

    async def do_it(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        note: Note,
    ) -> None:
        """Execute the command's action."""
        subnotes = await uow.note_repository.find_all_with_filters(
            parent_ref_id=note.ref_id,
            allow_archived=True,
            filter_parent_note_ref_ids=[note.ref_id],
        )

        for subnote in subnotes:
            await self.do_it(uow, progress_reporter, subnote)

        await uow.note_repository.remove(note.ref_id)
        await progress_reporter.mark_removed(note)

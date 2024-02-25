"""Archive a doc."""

from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_archive_service import (
    NoteArchiveService,
)
from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter


class DocArchiveService:
    """A service for removing a doc."""

    async def do_it(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        doc: Doc,
    ) -> None:
        """Execute the command's action."""
        if doc.archived:
            return

        subdocs = await uow.get_for(Doc).find_all_generic(
            parent_ref_id=doc.doc_collection.ref_id,
            allow_archived=True,
            parent_doc_ref_id=[doc.ref_id],
        )

        for subdoc in subdocs:
            await self.do_it(ctx, uow, progress_reporter, subdoc)

        note_archive_service = NoteArchiveService()
        await note_archive_service.archive_for_source(
            ctx, uow, NoteDomain.DOC, doc.ref_id
        )

        doc = doc.mark_archived(ctx)
        await uow.get_for(Doc).save(doc)
        await progress_reporter.mark_updated(doc)

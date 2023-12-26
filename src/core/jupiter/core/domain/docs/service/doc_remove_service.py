"""Remove a doc."""
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_remove_service import NoteRemoveService
from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.use_case import ProgressReporter


class DocRemoveService:
    """A service for removing a doc."""

    async def do_it(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        doc: Doc,
    ) -> None:
        """Execute the command's action."""
        subdocs = await uow.doc_repository.find_all_with_filters(
            parent_ref_id=doc.doc_collection_ref_id,
            allow_archived=True,
            filter_parent_doc_ref_ids=[doc.ref_id],
        )

        for subdoc in subdocs:
            await self.do_it(ctx, uow, progress_reporter, subdoc)

        note_remove_service = NoteRemoveService()
        await note_remove_service.remove_for_source(
            ctx, uow, NoteDomain.DOC, doc.ref_id
        )

        await uow.doc_repository.remove(doc.ref_id)
        await progress_reporter.mark_removed(doc)

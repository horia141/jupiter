"""Use case for creating a doc."""
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_content_block import OneOfNoteContentBlock
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.docs.doc_collection import DocCollection
from jupiter.core.domain.docs.doc_name import DocName
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class DocCreateArgs(UseCaseArgsBase):
    """DocCreate args."""

    name: DocName
    content: list[OneOfNoteContentBlock]
    parent_doc_ref_id: EntityId | None


@use_case_result
class DocCreateResult(UseCaseResultBase):
    """DocCreate result."""

    new_doc: Doc
    new_note: Note


@mutation_use_case(WorkspaceFeature.DOCS, exclude_app=[EventSource.CLI])
class DocCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[DocCreateArgs, DocCreateResult]
):
    """Use case for creating a doc."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: DocCreateArgs,
    ) -> DocCreateResult:
        """Execute the command's action."""
        workspace = context.workspace
        doc_collection = await uow.get_for(DocCollection).load_by_parent(
            workspace.ref_id
        )
        note_collection = await uow.get_for(NoteCollection).load_by_parent(
            workspace.ref_id
        )

        doc = Doc.new_doc(
            ctx=context.domain_context,
            doc_collection_ref_id=doc_collection.ref_id,
            parent_doc_ref_id=args.parent_doc_ref_id,
            name=args.name,
        )
        doc = await uow.get_for(Doc).create(doc)

        note = Note.new_note(
            ctx=context.domain_context,
            note_collection_ref_id=note_collection.ref_id,
            domain=NoteDomain.DOC,
            source_entity_ref_id=doc.ref_id,
            content=args.content,
        )
        note = await uow.get_for(Note).create(note)

        await progress_reporter.mark_created(doc)

        return DocCreateResult(new_doc=doc, new_note=note)

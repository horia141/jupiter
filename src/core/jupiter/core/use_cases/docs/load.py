"""Load a particulr doc."""

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    use_case_result,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseResultBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class DocLoadArgs(UseCaseArgsBase):
    """DocLoad args."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class DocLoadResult(UseCaseResultBase):
    """DocLoad result."""

    doc: Doc
    note: Note
    subdocs: list[Doc]


@readonly_use_case(WorkspaceFeature.DOCS)
class DocLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[DocLoadArgs, DocLoadResult]
):
    """Use case for loading a particular doc."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: DocLoadArgs,
    ) -> DocLoadResult:
        """Execute the command's action."""
        doc = await uow.doc_repository.load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        note = await uow.note_repository.load_for_source(
            NoteDomain.DOC, doc.ref_id, allow_archived=args.allow_archived
        )
        subdocs = await uow.doc_repository.find_all_with_filters(
            parent_ref_id=doc.doc_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_parent_doc_ref_ids=[doc.ref_id],
        )
        return DocLoadResult(doc, note, subdocs)

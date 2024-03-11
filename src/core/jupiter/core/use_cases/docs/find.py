"""The use case for finding docs."""
from collections import defaultdict

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.docs.doc_collection import DocCollection
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import NoFilter
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
    use_case_result_part,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class DocFindArgs(UseCaseArgsBase):
    """DocFind args."""

    include_notes: bool
    allow_archived: bool
    include_subdocs: bool
    filter_ref_ids: list[EntityId] | None = None


@use_case_result_part
class DocFindResultEntry(UseCaseResultBase):
    """A single entry in the load all docs response."""

    doc: Doc
    note: Note | None
    subdocs: list[Doc] | None = None


@use_case_result
class DocFindResult(UseCaseResultBase):
    """The result."""

    entries: list[DocFindResultEntry]


@readonly_use_case(WorkspaceFeature.DOCS, exclude_app=[EventSource.CLI])
class DocFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[DocFindArgs, DocFindResult]
):
    """The use case for finding docs."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: DocFindArgs,
    ) -> DocFindResult:
        """Execute the command's action."""
        workspace = context.workspace
        doc_collection = await uow.get_for(DocCollection).load_by_parent(
            workspace.ref_id
        )

        docs = await uow.get_for(Doc).find_all_generic(
            parent_ref_id=doc_collection.ref_id,
            allow_archived=args.allow_archived,
            ref_id=args.filter_ref_ids or NoFilter(),
            parent_doc_ref_id=NoFilter(),
        )

        notes_by_doc_ref_id: defaultdict[EntityId, Note] = defaultdict(None)
        if args.include_notes:
            note_collection = await uow.get_for(NoteCollection).load_by_parent(
                workspace.ref_id
            )
            notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.DOC,
                allow_archived=True,
                source_entity_ref_id=[d.ref_id for d in docs],
            )
            for n in notes:
                notes_by_doc_ref_id[n.source_entity_ref_id] = n

        subdocs_by_parent_ref_id = defaultdict(list)
        if args.include_subdocs:
            subdocs = await uow.get_for(Doc).find_all_generic(
                parent_ref_id=doc_collection.ref_id,
                allow_archived=args.allow_archived,
                parent_doc_ref_id=[d.ref_id for d in docs],
            )
            for sd in subdocs:
                if sd.parent_doc_ref_id is None:
                    continue
                subdocs_by_parent_ref_id[sd.parent_doc_ref_id].append(sd)

        return DocFindResult(
            entries=[
                DocFindResultEntry(
                    doc=doc,
                    note=notes_by_doc_ref_id.get(doc.ref_id, None),
                    subdocs=subdocs_by_parent_ref_id.get(doc.ref_id, None),
                )
                for doc in docs
            ]
        )

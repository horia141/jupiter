"""The use case for finding docs."""
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, List, Optional

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@dataclass
class DocFindArgs(UseCaseArgsBase):
    """DocFind args."""

    include_notes: bool
    allow_archived: bool
    include_subdocs: bool
    filter_ref_ids: Optional[List[EntityId]] = None


@dataclass
class DocFindResultEntry:
    """A single entry in the load all docs response."""

    doc: Doc
    note: Note | None = None
    subdocs: list[Doc] | None = None


@dataclass
class DocFindResult(UseCaseResultBase):
    """The result."""

    entries: List[DocFindResultEntry]


class DocFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[DocFindArgs, DocFindResult]
):
    """The use case for finding docs."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.DOCS

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: DocFindArgs,
    ) -> DocFindResult:
        """Execute the command's action."""
        workspace = context.workspace
        doc_collection = await uow.doc_collection_repository.load_by_parent(
            workspace.ref_id
        )

        docs = await uow.doc_repository.find_all_with_filters(
            parent_ref_id=doc_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
            filter_parent_doc_ref_ids=[None],
        )

        notes_by_doc_ref_id: defaultdict[EntityId, Note] = defaultdict(None)
        if args.include_notes:
            note_collection = await uow.note_collection_repository.load_by_parent(
                workspace.ref_id
            )
            notes = await uow.note_repository.find_all_with_filters(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.DOC,
                allow_archived=args.allow_archived,
                filter_source_entity_ref_ids=[d.ref_id for d in docs],
            )
            for n in notes:
                notes_by_doc_ref_id[n.source_entity_ref_id] = n

        subdocs_by_parent_ref_id = defaultdict(list)
        if args.include_subdocs:
            subdocs = await uow.doc_repository.find_all_with_filters(
                parent_ref_id=doc_collection.ref_id,
                allow_archived=args.allow_archived,
                filter_parent_doc_ref_ids=[d.ref_id for d in docs],
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

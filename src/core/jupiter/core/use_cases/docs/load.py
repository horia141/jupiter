"""Load a particulr doc."""
from dataclasses import dataclass
from typing import Iterable

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
class DocLoadArgs(UseCaseArgsBase):
    """DocLoad args."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class DocLoadResult(UseCaseResultBase):
    """DocLoad result."""

    doc: Doc
    note: Note
    subdocs: list[Doc]


class DocLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[DocLoadArgs, DocLoadResult]
):
    """Use case for loading a particular doc."""

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
        args: DocLoadArgs,
    ) -> DocLoadResult:
        """Execute the command's action."""
        doc = await uow.doc_repository.load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        note = await uow.note_repository.load_for_source(NoteDomain.DOC, doc.ref_id, allow_archived=args.allow_archived)
        subdocs = await uow.doc_repository.find_all_with_filters(
            parent_ref_id=doc.doc_collection_ref_id,
            allow_archived=args.allow_archived,
            filter_parent_doc_ref_ids=[doc.ref_id],
        )
        return DocLoadResult(doc, note, subdocs)

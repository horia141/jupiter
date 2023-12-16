"""Use case for creating a doc."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_content_block import OneOfNoteContentBlock
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.docs.doc_name import DocName
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class DocCreateArgs(UseCaseArgsBase):
    """DocCreate args."""

    name: DocName
    content: list[OneOfNoteContentBlock]
    parent_doc_ref_id: EntityId | None = None


@dataclass
class DocCreateResult(UseCaseResultBase):
    """DocCreate result."""

    new_doc: Doc
    new_note: Note


class DocCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[DocCreateArgs, DocCreateResult]
):
    """Use case for creating a doc."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.DOCS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: DocCreateArgs,
    ) -> DocCreateResult:
        """Execute the command's action."""
        workspace = context.workspace
        doc_collection = await uow.doc_collection_repository.load_by_parent(
            workspace.ref_id
        )
        note_collection = await uow.note_collection_repository.load_by_parent(
            workspace.ref_id
        )

        doc = Doc.new_doc(
            doc_collection_ref_id=doc_collection.ref_id,
            parent_doc_ref_id=args.parent_doc_ref_id,
            name=args.name,
            source=EventSource.CLI,
            created_time=self._time_provider.get_current_time(),
        )
        doc = await uow.doc_repository.create(doc)

        note = Note.new_note(
            note_collection_ref_id=note_collection.ref_id,
            domain=NoteDomain.DOC,
            source_entity_ref_id=doc.ref_id,
            content=args.content,
            source=EventSource.CLI,
            created_time=self._time_provider.get_current_time(),
        )
        note = await uow.note_repository.create(note)

        await progress_reporter.mark_created(doc)

        return DocCreateResult(new_doc=doc, new_note=note)

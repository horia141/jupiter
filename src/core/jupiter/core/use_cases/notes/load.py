"""Load a particulr note."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.notes.note import Note
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@dataclass
class NoteLoadArgs(UseCaseArgsBase):
    """NoteLoad args."""

    ref_id: EntityId
    allow_archived: bool


@dataclass
class NoteLoadResult(UseCaseResultBase):
    """NoteLoad result."""

    note: Note
    subnotes: list[Note]


class NoteLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[NoteLoadArgs, NoteLoadResult]
):
    """Use case for loading a particular note."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.NOTES

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: NoteLoadArgs,
    ) -> NoteLoadResult:
        """Execute the command's action."""
        note = await uow.note_repository.load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        subnotes = await uow.note_repository.find_all_with_filters(
            parent_ref_id=note.note_collection_ref_id,
            source=note.source,
            allow_archived=args.allow_archived,
            filter_parent_note_ref_ids=[note.ref_id],
        )
        return NoteLoadResult(note, subnotes)

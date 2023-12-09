"""The use case for finding notes."""
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, List, Optional

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.notes.note import Note
from jupiter.core.domain.notes.note_source import NoteSource
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@dataclass
class NoteFindArgs(UseCaseArgsBase):
    """NoteFind args."""

    allow_archived: bool
    include_subnotes: bool
    filter_ref_ids: Optional[List[EntityId]] = None


@dataclass
class NoteFindResultEntry:
    """A single entry in the load all notes response."""

    note: Note
    subnotes: Optional[List[Note]] = None


@dataclass
class NoteFindResult(UseCaseResultBase):
    """The result."""

    entries: List[NoteFindResultEntry]


class NoteFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[NoteFindArgs, NoteFindResult]
):
    """The use case for finding notes."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.CHORES

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: NoteFindArgs,
    ) -> NoteFindResult:
        """Execute the command's action."""
        workspace = context.workspace
        note_collection = await uow.note_collection_repository.load_by_parent(
            workspace.ref_id
        )

        notes = await uow.note_repository.find_all_with_filters(
            parent_ref_id=note_collection.ref_id,
            source=NoteSource.USER,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
            filter_parent_note_ref_ids=[None],
        )

        subnotes_by_parent_ref_id = defaultdict(list)
        if args.include_subnotes:
            subnotes = await uow.note_repository.find_all_with_filters(
                parent_ref_id=note_collection.ref_id,
                source=NoteSource.USER,
                allow_archived=args.allow_archived,
                filter_parent_note_ref_ids=[n.ref_id for n in notes],
            )
            for n in subnotes:
                subnotes_by_parent_ref_id[n.parent_note_ref_id].append(n)

        return NoteFindResult(
            entries=[
                NoteFindResultEntry(
                    note=note, subnotes=subnotes_by_parent_ref_id.get(note.ref_id, None)
                )
                for note in notes
            ]
        )

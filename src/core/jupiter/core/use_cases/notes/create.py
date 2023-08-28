"""Use case for creating a note."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.notes.note import Note
from jupiter.core.domain.notes.note_content_block import OneOfNoteContentBlock
from jupiter.core.domain.notes.note_name import NoteName
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
class NoteCreateArgs(UseCaseArgsBase):
    """NoteCreate args."""

    name: NoteName
    content: list[OneOfNoteContentBlock]
    parent_note_ref_id: EntityId | None = None


@dataclass
class NoteCreateResult(UseCaseResultBase):
    """NoteCreate result."""

    new_note: Note


class NoteCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[NoteCreateArgs, NoteCreateResult]
):
    """Use case for creating a note."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.NOTES

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: NoteCreateArgs,
    ) -> NoteCreateResult:
        """Execute the command's action."""
        workspace = context.workspace
        note_collection = await uow.note_collection_repository.load_by_parent(
            workspace.ref_id
        )
        note = Note.new_note(
            note_collection_ref_id=note_collection.ref_id,
            parent_note_ref_id=args.parent_note_ref_id,
            name=args.name,
            content=args.content,
            source=EventSource.CLI,
            created_time=self._time_provider.get_current_time(),
        )
        note = await uow.note_repository.create(note)
        await progress_reporter.mark_created(note)
        return NoteCreateResult(new_note=note)

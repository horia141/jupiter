"""Update a note use case."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.notes.note_content_block import OneOfNoteContentBlock
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter, UseCaseArgsBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class NoteUpdateForEntityArgs(UseCaseArgsBase):
    """NoteUpdate args."""

    ref_id: EntityId
    content: UpdateAction[list[OneOfNoteContentBlock]]


class NoteUpdateForEntityUseCase(
    AppTransactionalLoggedInMutationUseCase[NoteUpdateForEntityArgs, None]
):
    """Update a note use case."""

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
        args: NoteUpdateForEntityArgs,
    ) -> None:
        """Execute the command's action."""
        note = await uow.note_repository.load_by_id(args.ref_id)
        note = note.update_for_entity(
            content=args.content,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )
        note = await uow.note_repository.save(note)
        await progress_reporter.mark_updated(note)

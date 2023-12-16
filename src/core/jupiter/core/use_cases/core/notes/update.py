"""Update a note use case."""
from dataclasses import dataclass

from jupiter.core.domain.core.notes.note_content_block import OneOfNoteContentBlock
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
class NoteUpdateArgs(UseCaseArgsBase):
    """NoteUpdate args."""

    ref_id: EntityId
    content: UpdateAction[list[OneOfNoteContentBlock]]


class NoteUpdateUseCase(AppTransactionalLoggedInMutationUseCase[NoteUpdateArgs, None]):
    """Update a note use case."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: NoteUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        note = await uow.note_repository.load_by_id(args.ref_id)
        note = note.update(
            content=args.content,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )
        note = await uow.note_repository.save(note)

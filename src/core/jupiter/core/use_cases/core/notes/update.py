"""Update a note use case."""

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_content_block import OneOfNoteContentBlock
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class NoteUpdateArgs(UseCaseArgsBase):
    """NoteUpdate args."""

    ref_id: EntityId
    content: UpdateAction[list[OneOfNoteContentBlock]]


@mutation_use_case(exclude_app=[EventSource.CLI])
class NoteUpdateUseCase(AppTransactionalLoggedInMutationUseCase[NoteUpdateArgs, None]):
    """Update a note use case."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: NoteUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        note = await uow.get_for(Note).load_by_id(args.ref_id)
        note = note.update(
            ctx=context.domain_context,
            content=args.content,
        )
        note = await uow.get_for(Note).save(note)

"""Use case for creating a note."""

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_content_block import OneOfNoteContentBlock
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class NoteCreateArgs(UseCaseArgsBase):
    """NoteCreate args."""

    domain: NoteDomain
    source_entity_ref_id: EntityId
    content: list[OneOfNoteContentBlock]


@use_case_result
class NoteCreateResult(UseCaseResultBase):
    """NoteCreate result."""

    new_note: Note


@mutation_use_case()
class NoteCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[NoteCreateArgs, NoteCreateResult]
):
    """Use case for creating a note."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: NoteCreateArgs,
    ) -> NoteCreateResult:
        """Execute the command's action."""
        workspace = context.workspace
        note_collection = await uow.note_collection_repository.load_by_parent(
            workspace.ref_id
        )
        note = Note.new_note(
            ctx=context.domain_context,
            note_collection_ref_id=note_collection.ref_id,
            domain=args.domain,
            source_entity_ref_id=args.source_entity_ref_id,
            content=args.content,
        )
        note = await uow.note_repository.create(note)
        return NoteCreateResult(new_note=note)

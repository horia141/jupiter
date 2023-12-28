"""The command for removing a note."""

from jupiter.core.domain.core.notes.service.note_remove_service import (
    NoteRemoveService,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    use_case_args,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class NoteRemoveArgs(UseCaseArgsBase):
    """NoteRemove arguments."""

    ref_id: EntityId


@mutation_use_case()
class NoteRemoveUseCase(AppTransactionalLoggedInMutationUseCase[NoteRemoveArgs, None]):
    """The command for removing a note."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: NoteRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        note = await uow.note_repository.load_by_id(args.ref_id)
        await NoteRemoveService().remove(context.domain_context, uow, note)

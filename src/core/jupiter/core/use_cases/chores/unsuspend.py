"""The command for unsuspending a chore."""

from jupiter.core.domain.features import WorkspaceFeature
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
class ChoreUnsuspendArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.CHORES)
class ChoreUnsuspendUseCase(
    AppTransactionalLoggedInMutationUseCase[ChoreUnsuspendArgs, None]
):
    """The command for unsuspending a chore."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ChoreUnsuspendArgs,
    ) -> None:
        """Execute the command's action."""
        chore = await uow.chore_repository.load_by_id(args.ref_id)
        chore = chore.unsuspend(context.domain_context)
        await uow.chore_repository.save(chore)
        await progress_reporter.mark_updated(chore)

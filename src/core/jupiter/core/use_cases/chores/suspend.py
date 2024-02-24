"""The command for suspend a chore."""

from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
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
class ChoreSuspendArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.CHORES)
class ChoreSuspendUseCase(
    AppTransactionalLoggedInMutationUseCase[ChoreSuspendArgs, None]
):
    """The command for suspending a chore."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ChoreSuspendArgs,
    ) -> None:
        """Execute the command's action."""
        chore = await uow.repository_for(Chore).load_by_id(args.ref_id)
        chore = chore.suspend(context.domain_context)
        await uow.repository_for(Chore).save(chore)
        await progress_reporter.mark_updated(chore)

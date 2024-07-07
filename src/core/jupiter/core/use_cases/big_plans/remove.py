"""The command for removing a big plan."""

from jupiter.core.domain.concept.big_plans.service.remove_service import BigPlanRemoveService
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
class BigPlanRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.BIG_PLANS)
class BigPlanRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[BigPlanRemoveArgs, None]
):
    """The command for removing a big plan."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: BigPlanRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await BigPlanRemoveService().remove(
            context.domain_context,
            uow,
            progress_reporter,
            context.workspace,
            args.ref_id,
        )

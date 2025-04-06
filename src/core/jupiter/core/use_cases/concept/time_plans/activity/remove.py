"""Use case for removing a time plan activity."""

from jupiter.core.domain.concept.time_plans.time_plan_activity import TimePlanActivity
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_crown_remover import generic_crown_remover
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
class TimePlanActivityRemoveArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanActivityRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[TimePlanActivityRemoveArgs, None]
):
    """Use case for removing a time plan activity."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimePlanActivityRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await generic_crown_remover(
            context.domain_context,
            uow,
            progress_reporter,
            TimePlanActivity,
            args.ref_id,
        )

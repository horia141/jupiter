"""Use case for loading big plan milestones."""

from jupiter.core.domain.concept.big_plans.big_plan_milestone import (
    BigPlanMilestone,
)
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class BigPlanMilestoneLoadArgs(UseCaseArgsBase):
    """BigPlanMilestoneLoadArgs."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class BigPlanMilestoneLoadResult(UseCaseResultBase):
    """BigPlanMilestoneLoadResult."""

    big_plan_milestone: BigPlanMilestone


@readonly_use_case(WorkspaceFeature.BIG_PLANS)
class BigPlanMilestoneLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        BigPlanMilestoneLoadArgs, BigPlanMilestoneLoadResult
    ]
):
    """The use case for loading a particular big plan milestone."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: BigPlanMilestoneLoadArgs,
    ) -> BigPlanMilestoneLoadResult:
        """Execute the command's action."""
        big_plan_milestone = await uow.get_for(BigPlanMilestone).load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )

        return BigPlanMilestoneLoadResult(
            big_plan_milestone=big_plan_milestone,
        )

"""Use case for creating a time plan activity for an big plan."""
from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.time_plans.time_plan import TimePlan
from jupiter.core.domain.time_plans.time_plan_activity import TimePlanActivity
from jupiter.core.domain.time_plans.time_plan_activity_feasability import (
    TimePlanActivityFeasability,
)
from jupiter.core.domain.time_plans.time_plan_activity_kind import TimePlanActivityKind
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import (
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
class TimePlanActivityCreateForBigPlanArgs(UseCaseArgsBase):
    """Args."""

    time_plan_ref_id: EntityId
    big_plan_ref_id: EntityId
    kind: TimePlanActivityKind
    feasability: TimePlanActivityFeasability


@use_case_result
class TimePlanActivityCreateForBigPlanResult(UseCaseResultBase):
    """Result."""

    new_time_plan_activity: TimePlanActivity


@mutation_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanActivityCreateForBigPlanUseCase(
    AppTransactionalLoggedInMutationUseCase[
        TimePlanActivityCreateForBigPlanArgs, TimePlanActivityCreateForBigPlanResult
    ]
):
    """Use case for creating a time plan activity from a big plan."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimePlanActivityCreateForBigPlanArgs,
    ) -> TimePlanActivityCreateForBigPlanResult:
        """Execute the command's actions."""
        _ = await uow.get_for(TimePlan).load_by_id(args.time_plan_ref_id)
        _ = await uow.get_for(BigPlan).load_by_id(args.big_plan_ref_id)

        new_time_plan_activity = TimePlanActivity.new_activity_for_big_plan(
            context.domain_context,
            time_plan_ref_id=args.time_plan_ref_id,
            big_plan_ref_id=args.big_plan_ref_id,
            kind=args.kind,
            feasability=args.feasability,
        )
        new_time_plan_activity = await generic_creator(
            uow, progress_reporter, new_time_plan_activity
        )

        return TimePlanActivityCreateForBigPlanResult(
            new_time_plan_activity=new_time_plan_activity
        )

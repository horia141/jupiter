"""Use case for creating time plan activities for big plans."""

from jupiter.core.domain.concept.big_plans.big_plan import BigPlan
from jupiter.core.domain.concept.time_plans.time_plan import TimePlan
from jupiter.core.domain.concept.time_plans.time_plan_activity import (
    TimePlanActivity,
    TimePlanAlreadyAssociatedWithTargetError,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity_feasability import (
    TimePlanActivityFeasability,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity_kind import (
    TimePlanActivityKind,
)
from jupiter.core.domain.concept.time_plans.time_plan_domain import TimePlanDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
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
class TimePlanAssociateBigPlanWithPlanArgs(UseCaseArgsBase):
    """Args."""

    big_plan_ref_id: EntityId
    time_plan_ref_ids: list[EntityId]
    kind: TimePlanActivityKind
    feasability: TimePlanActivityFeasability


@use_case_result
class TimePlanAssociateBigPlanWithPlanResult(UseCaseResultBase):
    """Result."""

    new_time_plan_activities: list[TimePlanActivity]


@mutation_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanAssociateBigPlanWithPlanUseCase(
    AppTransactionalLoggedInMutationUseCase[
        TimePlanAssociateBigPlanWithPlanArgs, TimePlanAssociateBigPlanWithPlanResult
    ]
):
    """Use case for creating activities starting from a big plan."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimePlanAssociateBigPlanWithPlanArgs,
    ) -> TimePlanAssociateBigPlanWithPlanResult:
        """Execute the command's actions."""
        if len(args.time_plan_ref_ids) == 0:
            raise InputValidationError("You must specify some time plans")

        workspace = context.workspace
        time_plan_domain = await uow.get_for(TimePlanDomain).load_by_parent(
            workspace.ref_id
        )

        big_plan = await uow.get_for(BigPlan).load_by_id(args.big_plan_ref_id)

        time_plans = await uow.get_for(TimePlan).find_all(
            parent_ref_id=time_plan_domain.ref_id,
            allow_archived=False,
            filter_ref_ids=args.time_plan_ref_ids,
        )

        latest_time_plan = max(time_plans, key=lambda x: x.end_date)

        new_time_plan_activities = []

        for time_plan in time_plans:
            try:
                new_time_plan_activity = TimePlanActivity.new_activity_for_big_plan(
                    context.domain_context,
                    time_plan_ref_id=time_plan.ref_id,
                    big_plan_ref_id=big_plan.ref_id,
                    kind=args.kind,
                    feasability=args.feasability,
                )
                new_time_plan_activity = await generic_creator(
                    uow, progress_reporter, new_time_plan_activity
                )
                new_time_plan_activities.append(new_time_plan_activity)
            except TimePlanAlreadyAssociatedWithTargetError:
                # We were already working on this plan, no need to panic
                pass

        if big_plan.actionable_date is None or big_plan.due_date is None:
            big_plan = big_plan.change_dates_via_time_plan(
                context.domain_context,
                actionable_date=latest_time_plan.start_date,
                due_date=latest_time_plan.end_date,
            )
            await uow.get_for(BigPlan).save(big_plan)
            await progress_reporter.mark_updated(big_plan)

        return TimePlanAssociateBigPlanWithPlanResult(
            new_time_plan_activities=new_time_plan_activities
        )

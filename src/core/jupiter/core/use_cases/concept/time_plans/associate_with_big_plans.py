"""Use case for creating time plan actitivities for big plans."""
from jupiter.core.domain.concept.big_plans.big_plan import BigPlan
from jupiter.core.domain.concept.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.concept.time_plans.time_plan import TimePlan
from jupiter.core.domain.concept.time_plans.time_plan_activity import TimePlanActivity
from jupiter.core.domain.concept.time_plans.time_plan_activity_feasability import (
    TimePlanActivityFeasability,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity_kind import (
    TimePlanActivityKind,
)
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
class TimePlanAssociateWithBigPlansArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    big_plan_ref_ids: list[EntityId]
    override_existing_dates: bool
    kind: TimePlanActivityKind
    feasability: TimePlanActivityFeasability


@use_case_result
class TimePlanAssociateWithBigPlansResult(UseCaseResultBase):
    """Result."""

    new_time_plan_activities: list[TimePlanActivity]


@mutation_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanAssociateWithBigPlansUseCase(
    AppTransactionalLoggedInMutationUseCase[
        TimePlanAssociateWithBigPlansArgs, TimePlanAssociateWithBigPlansResult
    ]
):
    """Use case for creating activities starting from big plans."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimePlanAssociateWithBigPlansArgs,
    ) -> TimePlanAssociateWithBigPlansResult:
        """Execute the command's actions."""
        if len(args.big_plan_ref_ids) == 0:
            raise InputValidationError("You must specifiy some big plans")

        workspace = context.workspace

        time_plan = await uow.get_for(TimePlan).load_by_id(args.ref_id)

        big_plan_collection = await uow.get_for(BigPlanCollection).load_by_parent(
            workspace.ref_id
        )
        big_plans = await uow.get_for(BigPlan).find_all(
            parent_ref_id=big_plan_collection.ref_id,
            allow_archived=False,
            filter_ref_ids=args.big_plan_ref_ids,
        )

        new_time_plan_actitivies = []

        for big_plan in big_plans:
            new_time_plan_activity = TimePlanActivity.new_activity_for_big_plan(
                context.domain_context,
                time_plan_ref_id=args.ref_id,
                big_plan_ref_id=big_plan.ref_id,
                kind=args.kind,
                feasability=args.feasability,
            )
            new_time_plan_activity = await generic_creator(
                uow, progress_reporter, new_time_plan_activity
            )
            new_time_plan_actitivies.append(new_time_plan_activity)

            if (
                big_plan.actionable_date is None or big_plan.due_date is None
            ) or args.override_existing_dates:
                big_plan = big_plan.change_dates_via_time_plan(
                    context.domain_context,
                    actionable_date=time_plan.start_date,
                    due_date=time_plan.end_date,
                )
                await uow.get_for(BigPlan).save(big_plan)
                await progress_reporter.mark_updated(big_plan)

        return TimePlanAssociateWithBigPlansResult(
            new_time_plan_activities=new_time_plan_actitivies
        )

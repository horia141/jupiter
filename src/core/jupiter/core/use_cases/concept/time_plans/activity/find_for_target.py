"""The use case for finding the time plan activities for a particular target."""
from jupiter.core.domain.concept.time_plans.time_plan import TimePlan
from jupiter.core.domain.concept.time_plans.time_plan_activity import TimePlanActivity
from jupiter.core.domain.concept.time_plans.time_plan_activity_target import (
    TimePlanActivityTarget,
)
from jupiter.core.domain.concept.time_plans.time_plan_domain import TimePlanDomain
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
class TimePlanActivityFindForTargetArgs(UseCaseArgsBase):
    """Args."""

    allow_archived: bool
    target: TimePlanActivityTarget
    target_ref_id: EntityId


@use_case_result
class TimePlanActivityFindForTargetResultEntry(UseCaseResultBase):
    """Result."""

    time_plan: TimePlan
    time_plan_activity: TimePlanActivity


@use_case_result
class TimePlanActivityFindForTargetResult(UseCaseResultBase):
    """Result."""

    entries: list[TimePlanActivityFindForTargetResultEntry]


@readonly_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanActivityFindForTargetUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        TimePlanActivityFindForTargetArgs, TimePlanActivityFindForTargetResult
    ]
):
    """The command for finding time plan activities for a particular target."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: TimePlanActivityFindForTargetArgs,
    ) -> TimePlanActivityFindForTargetResult:
        workspace = context.workspace
        time_plan_domain = await uow.get_for(TimePlanDomain).load_by_parent(
            workspace.ref_id
        )

        time_plan_activities = await uow.get_for(TimePlanActivity).find_all_generic(
            parent_ref_id=None,
            allow_archived=args.allow_archived,
            target=args.target,
            target_ref_id=args.target_ref_id,
        )
        if len(time_plan_activities) > 0:
            time_plans = await uow.get_for(TimePlan).find_all_generic(
                parent_ref_id=time_plan_domain.ref_id,
                allow_archived=args.allow_archived,
                ref_id=[activity.time_plan.ref_id for activity in time_plan_activities],
            )
        else:
            time_plans = []
        time_plans_by_ref_id = {time_plan.ref_id: time_plan for time_plan in time_plans}

        return TimePlanActivityFindForTargetResult(
            entries=[
                TimePlanActivityFindForTargetResultEntry(
                    time_plan=time_plans_by_ref_id[activity.time_plan.ref_id],
                    time_plan_activity=activity,
                )
                for activity in time_plan_activities
            ]
        )

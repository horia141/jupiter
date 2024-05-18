"""Retrieve details about a time plan."""
from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.infra.generic_loader import generic_loader
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.time_plans.time_plan import TimePlan, TimePlanRepository
from jupiter.core.domain.time_plans.time_plan_activity import TimePlanActivity
from jupiter.core.domain.time_plans.time_plan_activity_target import (
    TimePlanActivityTarget,
)
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
class TimePlanLoadArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    allow_archived: bool


@use_case_result
class TimePlanLoadResult(UseCaseResultBase):
    """Result."""

    time_plan: TimePlan
    note: Note
    activities: list[TimePlanActivity]
    target_inbox_tasks: list[InboxTask]
    target_big_plans: list[BigPlan] | None
    sub_period_time_plans: list[TimePlan]
    previous_time_plan: TimePlan | None


@readonly_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[TimePlanLoadArgs, TimePlanLoadResult]
):
    """The command for loading details about a time plan."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: TimePlanLoadArgs,
    ) -> TimePlanLoadResult:
        """Execute the command's actions."""
        workspace = context.workspace

        time_plan, activities, note = await generic_loader(
            uow,
            TimePlan,
            args.ref_id,
            TimePlan.activities,
            TimePlan.note,
            allow_archived=args.allow_archived,
        )

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id
        )
        target_inbox_tasks = await uow.get_for(InboxTask).find_all(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            filter_ref_ids=[
                a.target_ref_id
                for a in activities
                if a.target == TimePlanActivityTarget.INBOX_TASK
            ],
        )

        target_big_plans = None
        if workspace.is_feature_available(WorkspaceFeature.BIG_PLANS):
            big_plan_collection = await uow.get_for(BigPlanCollection).load_by_parent(
                workspace.ref_id
            )
            target_big_plans = await uow.get_for(BigPlan).find_all(
                parent_ref_id=big_plan_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=[
                    a.target_ref_id
                    for a in activities
                    if a.target == TimePlanActivityTarget.BIG_PLAN
                ],
            )

        schedule = schedules.get_schedule(
            period=time_plan.period,
            name=time_plan.name,
            right_now=time_plan.right_now.to_timestamp_at_end_of_day(),
        )

        sub_period_time_plans = await uow.get(TimePlanRepository).find_all_in_range(
            parent_ref_id=time_plan.time_plan_domain.ref_id,
            allow_archived=False,
            filter_periods=time_plan.period.all_smaller_periods,
            filter_start_date=schedule.first_day,
            filter_end_date=schedule.end_day,
        )

        previous_time_plan = await uow.get(TimePlanRepository).find_previous(
            parent_ref_id=time_plan.time_plan_domain.ref_id,
            allow_archived=False,
            period=time_plan.period,
            right_now=time_plan.right_now
        )

        return TimePlanLoadResult(
            time_plan=time_plan,
            note=note,
            activities=list(activities),
            target_inbox_tasks=target_inbox_tasks,
            target_big_plans=target_big_plans,
            sub_period_time_plans=sub_period_time_plans,
            previous_time_plan=previous_time_plan
        )

"""Retrieve details about a time plan."""
from collections import defaultdict
from typing import cast

from jupiter.core.domain.concept.big_plans.big_plan import BigPlan, BigPlanRepository
from jupiter.core.domain.concept.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.time_plans.time_plan import (
    TimePlan,
    TimePlanRepository,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity import TimePlanActivity
from jupiter.core.domain.concept.time_plans.time_plan_activity_kind import (
    TimePlanActivityKind,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity_target import (
    TimePlanActivityTarget,
)
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_loader import generic_loader
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
class TimePlanLoadArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    allow_archived: bool
    include_targets: bool
    include_completed_nontarget: bool
    include_other_time_plans: bool


@use_case_result
class TimePlanLoadResult(UseCaseResultBase):
    """Result."""

    time_plan: TimePlan
    note: Note
    activities: list[TimePlanActivity]
    target_inbox_tasks: list[InboxTask] | None
    target_big_plans: list[BigPlan] | None
    activity_doneness: dict[EntityId, bool] | None
    completed_nontarget_inbox_tasks: list[InboxTask] | None
    completed_nottarget_big_plans: list[BigPlan] | None
    sub_period_time_plans: list[TimePlan] | None
    higher_time_plan: TimePlan | None
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
            allow_subentity_archived=False,
        )

        schedule = schedules.get_schedule(
            period=time_plan.period,
            name=time_plan.name,
            right_now=time_plan.right_now.to_timestamp_at_end_of_day(),
        )

        target_inbox_tasks = None
        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id
        )
        if args.include_targets:
            target_inbox_tasks = await uow.get_for(InboxTask).find_all(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_ref_ids=[
                    a.target_ref_id
                    for a in activities
                    if a.target == TimePlanActivityTarget.INBOX_TASK
                ],
            )

        completed_nontarget_inbox_tasks = None
        if args.include_completed_nontarget and target_inbox_tasks is not None:

            # The rule here should be:
            # If this is a inbox task or big plan include it always
            # If this is a generated one, then:
            #    If the recurring_task_period is strictly higher than the time plan is we include it
            #    If the recurring_task_period is equal or lower than the time plan one we skip it
            # expressed as: (it.source in (user, big-plan)) or (it.period  in (*all_higher_periods)
            # But this is hard to express cause inbox_tasks don't yet remember the period
            # of their source entity. Inference from the timeline is hard in SQL, etc.
            completed_nontarget_inbox_tasks = await uow.get(
                InboxTaskRepository
            ).find_completed_in_range(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_start_completed_date=schedule.first_day,
                filter_end_completed_date=schedule.end_day,
                filter_include_sources=[InboxTaskSource.USER, InboxTaskSource.BIG_PLAN],
                filter_exclude_ref_ids=[it.ref_id for it in target_inbox_tasks],
            )

        target_big_plans = None
        completed_nontarget_big_plans = None
        if workspace.is_feature_available(WorkspaceFeature.BIG_PLANS):
            big_plan_collection = await uow.get_for(BigPlanCollection).load_by_parent(
                workspace.ref_id
            )

            if args.include_targets:
                target_big_plans = await uow.get_for(BigPlan).find_all(
                    parent_ref_id=big_plan_collection.ref_id,
                    allow_archived=True,
                    filter_ref_ids=[
                        a.target_ref_id
                        for a in activities
                        if a.target == TimePlanActivityTarget.BIG_PLAN
                    ],
                )

            if args.include_completed_nontarget and target_big_plans is not None:
                completed_nontarget_big_plans = await uow.get(
                    BigPlanRepository
                ).find_completed_in_range(
                    parent_ref_id=big_plan_collection.ref_id,
                    allow_archived=True,
                    filter_start_completed_date=schedule.first_day,
                    filter_end_completed_date=schedule.end_day,
                    filter_exclude_ref_ids=[bp.ref_id for bp in target_big_plans],
                )

        activity_doneness = None
        if args.include_targets:
            activity_doneness = {}
            target_inbox_tasks_by_ref_id = {
                it.ref_id: it for it in cast(list[InboxTask], target_inbox_tasks)
            }
            target_big_plans_by_ref_id = (
                {bp.ref_id: bp for bp in target_big_plans} if target_big_plans else {}
            )
            activities_by_big_plan_ref_id: defaultdict[
                EntityId, list[EntityId]
            ] = defaultdict(list)

            for activity in activities:
                if activity.target != TimePlanActivityTarget.INBOX_TASK:
                    continue

                inbox_task = target_inbox_tasks_by_ref_id[activity.target_ref_id]

                if activity.kind == TimePlanActivityKind.FINISH:
                    activity_doneness[activity.ref_id] = inbox_task.is_completed
                elif activity.kind == TimePlanActivityKind.MAKE_PROGRESS:
                    # A tricky business logic decision.
                    # It's quite often the case that we setup a time plan with an inbox
                    # task where we wish to make progress. But the progress we do is just
                    # a bit after the time plan is created. So we'd still wish to show
                    # this as "done" in whatever view we have. So we add a buffer of a
                    # month afterwards to capture this.
                    modified_in_time_plan = (
                        inbox_task.is_working_or_more
                        and time_plan.start_date.to_timestamp_at_start_of_day()
                        <= inbox_task.last_modified_time
                        and inbox_task.last_modified_time
                        <= time_plan.end_date.add_days(30).to_timestamp_at_end_of_day()
                    )
                    activity_doneness[activity.ref_id] = (
                        inbox_task.is_completed or modified_in_time_plan
                    )

                if inbox_task.source == InboxTaskSource.BIG_PLAN:
                    activities_by_big_plan_ref_id[
                        inbox_task.source_entity_ref_id_for_sure
                    ].append(activity.ref_id)

            for activity in activities:
                if activity.target != TimePlanActivityTarget.BIG_PLAN:
                    continue

                if activity.target_ref_id not in target_big_plans_by_ref_id:
                    activity_doneness[activity.ref_id] = True
                    continue

                big_plan = target_big_plans_by_ref_id[activity.target_ref_id]

                if activity.kind == TimePlanActivityKind.FINISH:
                    activity_doneness[activity.ref_id] = big_plan.is_completed
                elif activity.kind == TimePlanActivityKind.MAKE_PROGRESS:
                    # A tricky business logic decision.
                    # It's quite often the case that we setup a time plan with an inbox
                    # task where we wish to make progress. But the progress we do is just
                    # a bit after the time plan is created. So we'd still wish to show
                    # this as "done" in whatever view we have. So we add a buffer of a
                    # month afterwards to capture this.
                    modified_in_time_plan = (
                        big_plan.is_working_or_more
                        and time_plan.start_date.to_timestamp_at_start_of_day()
                        <= big_plan.last_modified_time
                        and big_plan.last_modified_time
                        <= time_plan.end_date.add_days(60).to_timestamp_at_end_of_day()
                    )
                    all_subactivities_are_done = (
                        all(
                            activity_doneness[a]
                            for a in activities_by_big_plan_ref_id[big_plan.ref_id]
                        )
                        if len(activities_by_big_plan_ref_id[big_plan.ref_id]) > 0
                        else False
                    )
                    activity_doneness[activity.ref_id] = (
                        big_plan.is_completed
                        or modified_in_time_plan
                        or all_subactivities_are_done
                    )

        sub_period_time_plans = None
        higher_time_plan = None
        previous_time_plan = None
        if args.include_other_time_plans:
            sub_period_time_plans = await uow.get(TimePlanRepository).find_all_in_range(
                parent_ref_id=time_plan.time_plan_domain.ref_id,
                allow_archived=False,
                filter_periods=time_plan.period.all_smaller_periods,
                filter_start_date=schedule.first_day,
                filter_end_date=schedule.end_day,
            )

            higher_time_plan = await uow.get(TimePlanRepository).find_higher(
                parent_ref_id=time_plan.time_plan_domain.ref_id,
                allow_archived=False,
                period=time_plan.period,
                right_now=time_plan.right_now,
            )

            previous_time_plan = await uow.get(TimePlanRepository).find_previous(
                parent_ref_id=time_plan.time_plan_domain.ref_id,
                allow_archived=False,
                period=time_plan.period,
                right_now=time_plan.right_now,
            )

        return TimePlanLoadResult(
            time_plan=time_plan,
            note=note,
            activities=list(activities),
            target_inbox_tasks=target_inbox_tasks,
            target_big_plans=target_big_plans,
            activity_doneness=activity_doneness,
            completed_nontarget_inbox_tasks=completed_nontarget_inbox_tasks,
            completed_nottarget_big_plans=completed_nontarget_big_plans,
            sub_period_time_plans=sub_period_time_plans,
            higher_time_plan=higher_time_plan,
            previous_time_plan=previous_time_plan,
        )

"""Use case for creating time plan actitivities for already existin activities."""
from typing import cast

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.time_plans.time_plan import TimePlan
from jupiter.core.domain.time_plans.time_plan_activity import (
    TimePlanActivity,
    TimePlanAlreadyAssociatedWithTargetError,
)
from jupiter.core.domain.time_plans.time_plan_activity_feasability import (
    TimePlanActivityFeasability,
)
from jupiter.core.domain.time_plans.time_plan_activity_kind import TimePlanActivityKind
from jupiter.core.domain.time_plans.time_plan_activity_target import (
    TimePlanActivityTarget,
)
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
class TimePlanAssociateWithActivitiesArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId
    other_time_plan_ref_id: EntityId
    activity_ref_ids: list[EntityId]
    override_existing_dates: bool


@use_case_result
class TimePlanAssociateWithActivitiesResult(UseCaseResultBase):
    """Result."""

    new_time_plan_activities: list[TimePlanActivity]


@mutation_use_case(WorkspaceFeature.TIME_PLANS)
class TimePlanAssociateWithActivitiesUseCase(
    AppTransactionalLoggedInMutationUseCase[
        TimePlanAssociateWithActivitiesArgs, TimePlanAssociateWithActivitiesResult
    ]
):
    """Use case for creating activities starting from already existin activities."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: TimePlanAssociateWithActivitiesArgs,
    ) -> TimePlanAssociateWithActivitiesResult:
        """Execute the command's actions."""
        if len(args.activity_ref_ids) == 0:
            raise InputValidationError("You must specifiy some activities")

        time_plan = await uow.get_for(TimePlan).load_by_id(args.ref_id)

        activities = await uow.get_for(TimePlanActivity).find_all(
            parent_ref_id=args.other_time_plan_ref_id,
            allow_archived=False,
            filter_ref_ids=args.activity_ref_ids,
        )

        new_time_plan_actitivies = []

        for activity in activities:
            if activity.target == TimePlanActivityTarget.INBOX_TASK:
                inbox_task = await uow.get_for(InboxTask).load_by_id(
                    activity.target_ref_id
                )

                new_time_plan_activity = TimePlanActivity.new_activity_from_existing(
                    context.domain_context,
                    time_plan_ref_id=args.ref_id,
                    existing_activity_name=activity.name,
                    existing_activity_target=activity.target,
                    existing_activity_target_ref_id=inbox_task.ref_id,
                    existing_activity_kind=activity.kind,
                    existing_activity_feasability=activity.feasability,
                )
                new_time_plan_activity = await generic_creator(
                    uow, progress_reporter, new_time_plan_activity
                )
                new_time_plan_actitivies.append(new_time_plan_activity)

                if inbox_task.allow_user_changes and (
                    inbox_task.due_date is None or args.override_existing_dates
                ):
                    inbox_task = inbox_task.change_due_date_via_time_plan(
                        context.domain_context, due_date=time_plan.end_date
                    )
                    await uow.get_for(InboxTask).save(inbox_task)
                    await progress_reporter.mark_updated(inbox_task)

                if inbox_task.source == InboxTaskSource.BIG_PLAN:
                    big_plan = await uow.get_for(BigPlan).load_by_id(
                        cast(EntityId, inbox_task.big_plan_ref_id)
                    )

                    try:
                        new_big_plan_time_plan_activity = (
                            TimePlanActivity.new_activity_for_big_plan(
                                context.domain_context,
                                time_plan_ref_id=args.ref_id,
                                big_plan_ref_id=big_plan.ref_id,
                                kind=TimePlanActivityKind.MAKE_PROGRESS,
                                feasability=TimePlanActivityFeasability.MUST_DO,
                            )
                        )
                        new_big_plan_time_plan_activity = await generic_creator(
                            uow, progress_reporter, new_big_plan_time_plan_activity
                        )
                        new_time_plan_actitivies.append(new_big_plan_time_plan_activity)

                        if (
                            big_plan.actionable_date is None
                            or big_plan.due_date is None
                        ):
                            big_plan = big_plan.change_dates_via_time_plan(
                                context.domain_context,
                                actionable_date=time_plan.start_date,
                                due_date=time_plan.end_date,
                            )
                            await uow.get_for(BigPlan).save(big_plan)
                            await progress_reporter.mark_updated(big_plan)
                    except TimePlanAlreadyAssociatedWithTargetError:
                        # We were already working on this plan, no need to panic
                        pass
            else:
                big_plan = await uow.get_for(BigPlan).load_by_id(activity.target_ref_id)

                new_time_plan_activity = TimePlanActivity.new_activity_from_existing(
                    context.domain_context,
                    time_plan_ref_id=args.ref_id,
                    existing_activity_name=activity.name,
                    existing_activity_target=activity.target,
                    existing_activity_target_ref_id=big_plan.ref_id,
                    existing_activity_kind=activity.kind,
                    existing_activity_feasability=activity.feasability,
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

        return TimePlanAssociateWithActivitiesResult(
            new_time_plan_activities=new_time_plan_actitivies
        )

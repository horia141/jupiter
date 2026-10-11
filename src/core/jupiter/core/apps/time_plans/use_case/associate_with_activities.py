"""Use case for creating time plan actitivities for already existin activities."""

from jupiter.core.app import AppCore
from jupiter.core.apps.big_plans.root import BigPlan
from jupiter.core.apps.chores.root import Chore
from jupiter.core.apps.chores.sub.stack.root import ChoreStack
from jupiter.core.apps.habits.sub.habit.root import Habit
from jupiter.core.apps.habits.sub.stack.root import HabitStack
from jupiter.core.apps.time_plans.root import TimePlan
from jupiter.core.apps.time_plans.sub.activity.feasability import (
    TimePlanActivityFeasability,
)
from jupiter.core.apps.time_plans.sub.activity.kind import (
    TimePlanActivityKind,
)
from jupiter.core.apps.time_plans.sub.activity.root import (
    TimePlanActivity,
    TimePlanAlreadyAssociatedWithTargetError,
)
from jupiter.core.apps.todo.root import TodoTask
from jupiter.core.common.sub.inbox_tasks.root import InboxTask
from jupiter.core.config import (
    JupiterLoggedInMutationContext,
)
from jupiter.core.crown_entity_support import (
    JupiterUpdateCrownEntityArgs,
    JupiterUpdateCrownEntityUseCase,
)
from jupiter.core.features import WorkspaceFeature
from jupiter.core.named_entity_tag import NamedEntityTag
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.entity_link import EntityLink
from jupiter.framework.errors import InputValidationError
from jupiter.framework.progress_reporter.reporter import ProgressReporter
from jupiter.framework.storage.repository import DomainUnitOfWork
from jupiter.framework.use_case import (
    mutation_use_case,
)
from jupiter.framework.use_case_io import (
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)


@use_case_args
class TimePlanAssociateWithActivitiesArgs(JupiterUpdateCrownEntityArgs):
    """Args."""

    ref_id: EntityId
    other_time_plan_ref_id: EntityId
    activity_ref_ids: list[EntityId]
    kind: TimePlanActivityKind
    feasability: TimePlanActivityFeasability
    override_existing_dates: bool


@use_case_result
class TimePlanAssociateWithActivitiesResult(UseCaseResultBase):
    """Result."""

    new_time_plan_activities: list[TimePlanActivity]


@mutation_use_case(
    WorkspaceFeature.TIME_PLANS, only_for_component=[AppCore.WEBUI, AppCore.API]
)
class TimePlanAssociateWithActivitiesUseCase(
    JupiterUpdateCrownEntityUseCase[
        TimePlanAssociateWithActivitiesArgs, TimePlanAssociateWithActivitiesResult
    ]
):
    """Use case for creating activities starting from already existin activities."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: JupiterLoggedInMutationContext,
        args: TimePlanAssociateWithActivitiesArgs,
    ) -> TimePlanAssociateWithActivitiesResult:
        """Execute the command's actions."""
        if len(args.activity_ref_ids) == 0:
            raise InputValidationError("You must specifiy some activities")

        time_plan = await self.load_entity(
            uow, context.user.ref_id, TimePlan, args.ref_id
        )

        await self.check_entity(
            uow, context.user.ref_id, TimePlan, args.other_time_plan_ref_id
        )

        activities = await self.find_all_entities(
            uow,
            context.user.ref_id,
            TimePlanActivity,
            args.activity_ref_ids,
            allow_archived=False,
        )

        new_time_plan_actitivies = []

        # First we create all the explicitly called out big plan activities.
        for activity in activities:
            if not activity.is_target_big_plan:
                continue

            big_plan = await self.load_entity(
                uow, context.user.ref_id, BigPlan, activity.target.ref_id
            )

            new_time_plan_activity = TimePlanActivity.new_activity_from_existing(
                context.domain_context,
                time_plan_ref_id=args.ref_id,
                existing_activity_name=activity.name,
                existing_activity_target=activity.target,
                existing_activity_kind=args.kind,
                existing_activity_feasability=args.feasability,
            )
            new_time_plan_activity = await self.create_entity(
                context.domain_context,
                uow,
                progress_reporter,
                context.user.ref_id,
                new_time_plan_activity,
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

        # Skip todo / inbox task activities if the target time plan does not allow them.
        if not time_plan.allows_inbox_tasks:
            return TimePlanAssociateWithActivitiesResult(
                new_time_plan_activities=new_time_plan_actitivies
            )

        # Then we create all the explicitly called out todo task activities.
        for activity in activities:
            if not activity.is_target_todo_task:
                continue

            await self.check_entity(
                uow, context.user.ref_id, TodoTask, activity.target.ref_id
            )

            new_time_plan_activity = TimePlanActivity.new_activity_from_existing(
                context.domain_context,
                time_plan_ref_id=args.ref_id,
                existing_activity_name=activity.name,
                existing_activity_target=activity.target,
                existing_activity_kind=args.kind,
                existing_activity_feasability=args.feasability,
            )
            new_time_plan_activity = await self.create_entity(
                context.domain_context,
                uow,
                progress_reporter,
                context.user.ref_id,
                new_time_plan_activity,
            )
            new_time_plan_actitivies.append(new_time_plan_activity)

            inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=None,
                allow_archived=False,
                owner=EntityLink.std(
                    NamedEntityTag.TODO_TASK.value, activity.target.ref_id
                ),
            )
            if len(inbox_tasks) == 0:
                continue

            inbox_task = inbox_tasks[0]
            if inbox_task.allow_user_changes and (
                inbox_task.due_date is None or args.override_existing_dates
            ):
                inbox_task = inbox_task.change_due_date_via_time_plan(
                    context.domain_context, due_date=time_plan.end_date
                )
                await uow.get_for(InboxTask).save(inbox_task)

        for activity in activities:
            if not activity.is_target_habit:
                continue

            habit = await self.load_entity(
                uow, context.user.ref_id, Habit, activity.target.ref_id
            )
            if habit.suspended:
                continue

            new_time_plan_activity = TimePlanActivity.new_activity_from_existing(
                context.domain_context,
                time_plan_ref_id=args.ref_id,
                existing_activity_name=activity.name,
                existing_activity_target=activity.target,
                existing_activity_kind=args.kind,
                existing_activity_feasability=args.feasability,
            )
            new_time_plan_activity = await self.create_entity(
                context.domain_context,
                uow,
                progress_reporter,
                context.user.ref_id,
                new_time_plan_activity,
            )
            new_time_plan_actitivies.append(new_time_plan_activity)

        for activity in activities:
            if not activity.is_target_habit_stack:
                continue

            await self.check_entity(
                uow, context.user.ref_id, HabitStack, activity.target.ref_id
            )

            new_time_plan_activity = TimePlanActivity.new_activity_from_existing(
                context.domain_context,
                time_plan_ref_id=args.ref_id,
                existing_activity_name=activity.name,
                existing_activity_target=activity.target,
                existing_activity_kind=args.kind,
                existing_activity_feasability=args.feasability,
            )
            new_time_plan_activity = await self.create_entity(
                context.domain_context,
                uow,
                progress_reporter,
                context.user.ref_id,
                new_time_plan_activity,
            )
            new_time_plan_actitivies.append(new_time_plan_activity)

        for activity in activities:
            if not activity.is_target_chore_stack:
                continue

            await self.check_entity(
                uow, context.user.ref_id, ChoreStack, activity.target.ref_id
            )

            new_time_plan_activity = TimePlanActivity.new_activity_from_existing(
                context.domain_context,
                time_plan_ref_id=args.ref_id,
                existing_activity_name=activity.name,
                existing_activity_target=activity.target,
                existing_activity_kind=args.kind,
                existing_activity_feasability=args.feasability,
            )
            new_time_plan_activity = await self.create_entity(
                context.domain_context,
                uow,
                progress_reporter,
                context.user.ref_id,
                new_time_plan_activity,
            )
            new_time_plan_actitivies.append(new_time_plan_activity)

        for activity in activities:
            if not activity.is_target_chore:
                continue

            chore = await self.load_entity(
                uow, context.user.ref_id, Chore, activity.target.ref_id
            )
            if chore.suspended:
                continue

            new_time_plan_activity = TimePlanActivity.new_activity_from_existing(
                context.domain_context,
                time_plan_ref_id=args.ref_id,
                existing_activity_name=activity.name,
                existing_activity_target=activity.target,
                existing_activity_kind=args.kind,
                existing_activity_feasability=args.feasability,
            )
            new_time_plan_activity = await self.create_entity(
                context.domain_context,
                uow,
                progress_reporter,
                context.user.ref_id,
                new_time_plan_activity,
            )
            new_time_plan_actitivies.append(new_time_plan_activity)

        for activity in activities:
            if not activity.is_target_inbox_task:
                continue

            inbox_task = await uow.get_for(InboxTask).load_by_id(activity.target.ref_id)

            new_time_plan_activity = TimePlanActivity.new_activity_from_existing(
                context.domain_context,
                time_plan_ref_id=args.ref_id,
                existing_activity_name=activity.name,
                existing_activity_target=activity.target,
                existing_activity_kind=args.kind,
                existing_activity_feasability=args.feasability,
            )
            new_time_plan_activity = await self.create_entity(
                context.domain_context,
                uow,
                progress_reporter,
                context.user.ref_id,
                new_time_plan_activity,
            )
            new_time_plan_actitivies.append(new_time_plan_activity)

            if inbox_task.allow_user_changes and (
                inbox_task.due_date is None or args.override_existing_dates
            ):
                inbox_task = inbox_task.change_due_date_via_time_plan(
                    context.domain_context, due_date=time_plan.end_date
                )
                await uow.get_for(InboxTask).save(inbox_task)

            if inbox_task.owner.the_type == NamedEntityTag.BIG_PLAN.value:
                big_plan = await self.load_entity(
                    uow, context.user.ref_id, BigPlan, inbox_task.owner.ref_id
                )

                try:
                    new_big_plan_time_plan_activity = (
                        TimePlanActivity.new_activity_for_big_plan(
                            context.domain_context,
                            time_plan_ref_id=args.ref_id,
                            big_plan_ref_id=big_plan.ref_id,
                            kind=TimePlanActivityKind.MAKE_PROGRESS,
                            feasability=TimePlanActivityFeasability.NICE_TO_HAVE,
                        )
                    )
                    new_big_plan_time_plan_activity = await self.create_entity(
                        context.domain_context,
                        uow,
                        progress_reporter,
                        context.user.ref_id,
                        new_big_plan_time_plan_activity,
                    )
                    new_time_plan_actitivies.append(new_big_plan_time_plan_activity)

                    if big_plan.actionable_date is None or big_plan.due_date is None:
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

        return TimePlanAssociateWithActivitiesResult(
            new_time_plan_activities=new_time_plan_actitivies
        )

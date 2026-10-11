"""Use case for creating time plan activities for habit stacks."""

from jupiter.core.app import AppCore
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
from jupiter.core.apps.time_plans.use_case.associate_with_habits import (
    dates_in_inclusive_range,
    inbox_task_overlaps_time_plan,
)
from jupiter.core.common.sub.access.access_level import AccessLevel
from jupiter.core.common.sub.inbox_tasks.root import InboxTask
from jupiter.core.config import (
    JupiterLoggedInMutationContext,
)
from jupiter.core.crown_entity_support import (
    JupiterUpdateCrownEntityArgs,
    JupiterUpdateCrownEntityUseCase,
)
from jupiter.core.features import WorkspaceFeature
from jupiter.core.gen.service.gen import GenService
from jupiter.core.named_entity_tag import NamedEntityTag
from jupiter.core.sync_target import SyncTarget
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
class TimePlanAssociateWithHabitStacksArgs(JupiterUpdateCrownEntityArgs):
    """Args."""

    ref_id: EntityId
    habit_stack_ref_ids: list[EntityId]
    kind: TimePlanActivityKind
    feasability: TimePlanActivityFeasability


@use_case_result
class TimePlanAssociateWithHabitStacksResult(UseCaseResultBase):
    """Result."""

    new_time_plan_activities: list[TimePlanActivity]


@mutation_use_case(
    WorkspaceFeature.TIME_PLANS, only_for_component=[AppCore.WEBUI, AppCore.API]
)
class TimePlanAssociateWithHabitStacksUseCase(
    JupiterUpdateCrownEntityUseCase[
        TimePlanAssociateWithHabitStacksArgs, TimePlanAssociateWithHabitStacksResult
    ]
):
    """Use case for creating activities starting from habit stacks."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: JupiterLoggedInMutationContext,
        args: TimePlanAssociateWithHabitStacksArgs,
    ) -> TimePlanAssociateWithHabitStacksResult:
        """Execute the command's actions."""
        if len(args.habit_stack_ref_ids) == 0:
            raise InputValidationError("You must specify some habit stacks")

        time_plan = await self.load_entity(
            uow, context.user.ref_id, TimePlan, args.ref_id
        )

        if not time_plan.allows_inbox_tasks:
            raise InputValidationError(
                "Habit stacks can only be added to daily or weekly time plans"
            )

        habit_stacks = await self.find_all_generic(
            uow,
            context.user.ref_id,
            HabitStack,
            allow_archived=False,
            ref_id=args.habit_stack_ref_ids,
            minimum_access_level=AccessLevel.READER,
        )

        member_habits = await uow.get_for(Habit).find_all_generic(
            parent_ref_id=None,
            allow_archived=False,
            stack_ref_id=args.habit_stack_ref_ids,
            suspended=False,
        )
        habits_by_stack_ref_id: dict[EntityId, list[Habit]] = {}
        for habit in member_habits:
            if habit.stack_ref_id is None:
                continue
            habits_by_stack_ref_id.setdefault(habit.stack_ref_id, []).append(habit)

        new_time_plan_activities = []

        for habit_stack in habit_stacks:
            try:
                new_stack_activity = TimePlanActivity.new_activity_for_habit_stack(
                    context.domain_context,
                    time_plan_ref_id=args.ref_id,
                    habit_stack_ref_id=habit_stack.ref_id,
                    kind=args.kind,
                    feasability=args.feasability,
                )
                new_stack_activity = await self.create_entity(
                    context.domain_context,
                    uow,
                    progress_reporter,
                    context.user.ref_id,
                    new_stack_activity,
                )
                new_time_plan_activities.append(new_stack_activity)
            except TimePlanAlreadyAssociatedWithTargetError:
                pass

            for habit in habits_by_stack_ref_id.get(habit_stack.ref_id, []):
                try:
                    new_habit_activity = TimePlanActivity.new_activity_for_habit(
                        context.domain_context,
                        time_plan_ref_id=args.ref_id,
                        habit_ref_id=habit.ref_id,
                        kind=args.kind,
                        feasability=args.feasability,
                    )
                    new_habit_activity = await self.create_entity(
                        context.domain_context,
                        uow,
                        progress_reporter,
                        context.user.ref_id,
                        new_habit_activity,
                    )
                    new_time_plan_activities.append(new_habit_activity)
                except TimePlanAlreadyAssociatedWithTargetError:
                    pass

                inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                    parent_ref_id=None,
                    allow_archived=False,
                    owner=EntityLink.std(NamedEntityTag.HABIT.value, habit.ref_id),
                )

                for inbox_task in inbox_tasks:
                    if not inbox_task_overlaps_time_plan(inbox_task, time_plan):
                        continue

                    try:
                        new_inbox_task_activity = (
                            TimePlanActivity.new_activity_for_inbox_task(
                                context.domain_context,
                                time_plan_ref_id=args.ref_id,
                                inbox_task_ref_id=inbox_task.ref_id,
                                kind=args.kind,
                                feasability=args.feasability,
                            )
                        )
                        new_inbox_task_activity = await self.create_entity(
                            context.domain_context,
                            uow,
                            progress_reporter,
                            context.user.ref_id,
                            new_inbox_task_activity,
                        )
                        new_time_plan_activities.append(new_inbox_task_activity)
                    except TimePlanAlreadyAssociatedWithTargetError:
                        pass

        return TimePlanAssociateWithHabitStacksResult(
            new_time_plan_activities=new_time_plan_activities
        )

    async def _perform_post_transactional_mutation_work(
        self,
        progress_reporter: ProgressReporter,
        context: JupiterLoggedInMutationContext,
        args: TimePlanAssociateWithHabitStacksArgs,
        result: TimePlanAssociateWithHabitStacksResult,
    ) -> None:
        """Generate inbox tasks covering the time plan, then attach the new ones."""
        async with self._ports.domain_storage_engine.get_unit_of_work() as uow:
            time_plan = await uow.get_for(TimePlan).load_by_id(args.ref_id)
            member_habits = await uow.get_for(Habit).find_all_generic(
                parent_ref_id=None,
                allow_archived=False,
                stack_ref_id=args.habit_stack_ref_ids,
                suspended=False,
            )
            habit_ref_ids = [habit.ref_id for habit in member_habits]

        if len(habit_ref_ids) == 0:
            return

        gen_service = GenService(
            self._ports.domain_storage_engine,
            self._concept_registry,
        )
        for day in dates_in_inclusive_range(time_plan.start_date, time_plan.end_date):
            await gen_service.do_it(
                context.domain_context,
                progress_reporter=progress_reporter,
                user=context.user,
                workspace=context.workspace,
                gen_even_if_not_modified=False,
                today=day,
                gen_targets=[SyncTarget.HABITS],
                period=None,
                filter_habit_ref_ids=habit_ref_ids,
            )

        async with self._ports.domain_storage_engine.get_unit_of_work() as uow:
            for habit_ref_id in habit_ref_ids:
                inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                    parent_ref_id=None,
                    allow_archived=False,
                    owner=EntityLink.std(NamedEntityTag.HABIT.value, habit_ref_id),
                )
                for inbox_task in inbox_tasks:
                    if not inbox_task_overlaps_time_plan(inbox_task, time_plan):
                        continue
                    try:
                        new_inbox_task_activity = (
                            TimePlanActivity.new_activity_for_inbox_task(
                                context.domain_context,
                                time_plan_ref_id=time_plan.ref_id,
                                inbox_task_ref_id=inbox_task.ref_id,
                                kind=args.kind,
                                feasability=args.feasability,
                            )
                        )
                        await self.create_entity(
                            context.domain_context,
                            uow,
                            progress_reporter,
                            context.user.ref_id,
                            new_inbox_task_activity,
                        )
                    except TimePlanAlreadyAssociatedWithTargetError:
                        pass

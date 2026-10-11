"""Use case for creating time plan activities for a habit."""

from jupiter.core.app import AppCore
from jupiter.core.apps.habits.sub.habit.root import Habit
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
from jupiter.core.common.sub.access.sub.status.service.load_for_acl import (
    LoadForAclService,
)
from jupiter.core.common.sub.inbox_tasks.root import InboxTask
from jupiter.core.config import (
    JupiterLoggedInMutationContext,
)
from jupiter.core.crown_entity_support import (
    JupiterCreateCrownEntityArgs,
    JupiterCreateCrownEntityUseCase,
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
class TimePlanAssociateHabitWithPlanArgs(JupiterCreateCrownEntityArgs):
    """Args."""

    habit_ref_id: EntityId
    time_plan_ref_ids: list[EntityId]
    kind: TimePlanActivityKind
    feasability: TimePlanActivityFeasability


@use_case_result
class TimePlanAssociateHabitWithPlanResult(UseCaseResultBase):
    """Result."""

    new_time_plan_activities: list[TimePlanActivity]


@mutation_use_case(
    WorkspaceFeature.TIME_PLANS, only_for_component=[AppCore.WEBUI, AppCore.API]
)
class TimePlanAssociateHabitWithPlanUseCase(
    JupiterCreateCrownEntityUseCase[
        TimePlanAssociateHabitWithPlanArgs, TimePlanAssociateHabitWithPlanResult
    ]
):
    """Use case for creating activities starting from a habit."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: JupiterLoggedInMutationContext,
        args: TimePlanAssociateHabitWithPlanArgs,
    ) -> TimePlanAssociateHabitWithPlanResult:
        """Execute the command's actions."""
        if len(args.time_plan_ref_ids) == 0:
            raise InputValidationError("You must specify some time plans")

        habit = await LoadForAclService().do_it(
            uow,
            Habit,
            args.habit_ref_id,
            context.user.ref_id,
            AccessLevel.READER,
        )

        if habit.suspended:
            raise InputValidationError(
                "Suspended habits cannot be added to a time plan"
            )

        time_plans = await self.find_all_entities(
            uow,
            context.user.ref_id,
            TimePlan,
            args.time_plan_ref_ids,
            allow_archived=False,
        )

        for time_plan in time_plans:
            if not time_plan.allows_inbox_tasks:
                raise InputValidationError(
                    f"Time plan {time_plan.name} does not allow habit activities"
                )

        inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=None,
            allow_archived=False,
            owner=EntityLink.std(NamedEntityTag.HABIT.value, habit.ref_id),
        )

        new_time_plan_activities = []

        for time_plan in time_plans:
            try:
                new_time_plan_activity = TimePlanActivity.new_activity_for_habit(
                    context.domain_context,
                    time_plan_ref_id=time_plan.ref_id,
                    habit_ref_id=habit.ref_id,
                    kind=args.kind,
                    feasability=args.feasability,
                )
                new_time_plan_activity = await self.create_entity(
                    context.domain_context,
                    uow,
                    progress_reporter,
                    context.user.ref_id,
                    new_time_plan_activity,
                )
                new_time_plan_activities.append(new_time_plan_activity)
            except TimePlanAlreadyAssociatedWithTargetError:
                # We were already working on this plan, no need to panic
                pass

            # The inbox tasks the habit already generated in the interval of the
            # time plan become activities of their own.
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
                    new_inbox_task_activity = await self.create_entity(
                        context.domain_context,
                        uow,
                        progress_reporter,
                        context.user.ref_id,
                        new_inbox_task_activity,
                    )
                    new_time_plan_activities.append(new_inbox_task_activity)
                except TimePlanAlreadyAssociatedWithTargetError:
                    # We were already working on this task, no need to panic
                    pass

        return TimePlanAssociateHabitWithPlanResult(
            new_time_plan_activities=new_time_plan_activities
        )

    async def _perform_post_transactional_mutation_work(
        self,
        progress_reporter: ProgressReporter,
        context: JupiterLoggedInMutationContext,
        args: TimePlanAssociateHabitWithPlanArgs,
        result: TimePlanAssociateHabitWithPlanResult,
    ) -> None:
        """Generate inbox tasks covering each time plan, then attach the new ones."""
        gen_service = GenService(
            self._ports.domain_storage_engine,
            self._concept_registry,
        )

        async with self._ports.domain_storage_engine.get_unit_of_work() as uow:
            time_plans = await uow.get_for(TimePlan).find_all_generic(
                parent_ref_id=None,
                allow_archived=False,
                ref_id=args.time_plan_ref_ids,
            )

        for time_plan in time_plans:
            for day in dates_in_inclusive_range(
                time_plan.start_date, time_plan.end_date
            ):
                await gen_service.do_it(
                    context.domain_context,
                    progress_reporter=progress_reporter,
                    user=context.user,
                    workspace=context.workspace,
                    gen_even_if_not_modified=False,
                    today=day,
                    gen_targets=[SyncTarget.HABITS],
                    period=None,
                    filter_habit_ref_ids=[args.habit_ref_id],
                )

            async with self._ports.domain_storage_engine.get_unit_of_work() as uow:
                inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                    parent_ref_id=None,
                    allow_archived=False,
                    owner=EntityLink.std(NamedEntityTag.HABIT.value, args.habit_ref_id),
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

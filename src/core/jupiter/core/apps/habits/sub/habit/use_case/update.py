"""The command for updating a habit."""

from jupiter.core.apps.habits.repeats_strategy import (
    HabitRepeatsStrategy,
)
from jupiter.core.apps.habits.sub.habit.name import HabitName
from jupiter.core.apps.habits.sub.habit.root import Habit
from jupiter.core.apps.habits.sub.stack.root import HabitStack
from jupiter.core.apps.life_plan.sub.aspects.root import Aspect
from jupiter.core.apps.life_plan.sub.chapters.root import Chapter
from jupiter.core.apps.life_plan.sub.goals.root import Goal
from jupiter.core.common.difficulty import Difficulty
from jupiter.core.common.eisen import Eisen
from jupiter.core.common.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.common.recurring_task_due_at_month import (
    RecurringTaskDueAtMonth,
)
from jupiter.core.common.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.common.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.common.scheduling_params import (
    Schedulability,
    build_scheduling_params_update,
)
from jupiter.core.config import (
    JupiterLoggedInMutationContext,
)
from jupiter.core.crown_entity_support import (
    JupiterUpdateCrownEntityArgs,
    JupiterUpdateCrownEntityUseCase,
)
from jupiter.core.features import WorkspaceFeature
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.errors import InputValidationError
from jupiter.framework.progress_reporter.reporter import ProgressReporter
from jupiter.framework.storage.repository import DomainUnitOfWork
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import (
    UnavailableForContextError,
    mutation_use_case,
)
from jupiter.framework.use_case_io import (
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)


@use_case_args
class HabitUpdateArgs(JupiterUpdateCrownEntityArgs):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[HabitName]
    aspect_ref_id: UpdateAction[EntityId]
    chapter_ref_id: UpdateAction[EntityId | None]
    goal_ref_id: UpdateAction[EntityId | None]
    stack_ref_id: UpdateAction[EntityId | None]
    is_key: UpdateAction[bool]
    eisen: UpdateAction[Eisen]
    difficulty: UpdateAction[Difficulty]
    actionable_from_day: UpdateAction[RecurringTaskDueAtDay | None]
    actionable_from_month: UpdateAction[RecurringTaskDueAtMonth | None]
    due_at_day: UpdateAction[RecurringTaskDueAtDay | None]
    due_at_month: UpdateAction[RecurringTaskDueAtMonth | None]
    skip_rule: UpdateAction[RecurringTaskSkipRule | None]
    repeats_strategy: UpdateAction[HabitRepeatsStrategy | None]
    repeats_in_period_count: UpdateAction[int | None]
    schedulability: UpdateAction[Schedulability]
    scheduling_event_duration_mins: UpdateAction[int | None]
    scheduling_event_count: UpdateAction[int | None]
    suspended: UpdateAction[bool]


@use_case_result
class HabitUpdateResult(UseCaseResultBase):
    """HabitUpdate result."""

    updated_habit: Habit


@mutation_use_case(WorkspaceFeature.HABITS)
class HabitUpdateUseCase(
    JupiterUpdateCrownEntityUseCase[HabitUpdateArgs, HabitUpdateResult]
):
    """The command for updating a habit.

    Only the habit itself changes. Its inbox tasks catch up the next time they are
    generated - via a regen, or the periodic gen run.
    """

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: JupiterLoggedInMutationContext,
        args: HabitUpdateArgs,
    ) -> HabitUpdateResult:
        """Execute the command's action."""
        workspace = context.workspace

        habit = await self.load_entity(uow, context.user.ref_id, Habit, args.ref_id)

        if not workspace.is_feature_available(WorkspaceFeature.LIFE_PLAN):
            if (
                args.aspect_ref_id.should_change
                and args.aspect_ref_id.just_the_value is not None
            ):
                raise UnavailableForContextError(WorkspaceFeature.LIFE_PLAN)
            if (
                args.chapter_ref_id.should_change
                and args.chapter_ref_id.just_the_value is not None
            ):
                raise UnavailableForContextError(WorkspaceFeature.LIFE_PLAN)
            if (
                args.goal_ref_id.should_change
                and args.goal_ref_id.just_the_value is not None
            ):
                raise UnavailableForContextError(WorkspaceFeature.LIFE_PLAN)

        if (
            args.eisen.should_change
            or args.difficulty.should_change
            or args.actionable_from_day.should_change
            or args.actionable_from_month.should_change
            or args.due_at_day.should_change
            or args.due_at_month.should_change
            or args.skip_rule.should_change
        ):
            habit_gen_params = UpdateAction.change_to(
                RecurringTaskGenParams(
                    habit.gen_params.period,
                    args.eisen.or_else(habit.gen_params.eisen),
                    args.difficulty.or_else(habit.gen_params.difficulty),
                    args.actionable_from_day.or_else(
                        habit.gen_params.actionable_from_day,
                    ),
                    args.actionable_from_month.or_else(
                        habit.gen_params.actionable_from_month,
                    ),
                    args.due_at_day.or_else(habit.gen_params.due_at_day),
                    args.due_at_month.or_else(habit.gen_params.due_at_month),
                    args.skip_rule.or_else(habit.gen_params.skip_rule),
                ),
            )
        else:
            habit_gen_params = UpdateAction.do_nothing()

        if workspace.is_feature_available(WorkspaceFeature.LIFE_PLAN):
            new_aspect_ref_id = args.aspect_ref_id.or_else(habit.aspect_ref_id)
            new_chapter_ref_id = args.chapter_ref_id.or_else(habit.chapter_ref_id)
            new_goal_ref_id = args.goal_ref_id.or_else(habit.goal_ref_id)
            aspect_changing = (
                args.aspect_ref_id.should_change
                and new_aspect_ref_id != habit.aspect_ref_id
            )
            chapter_changing = (
                args.chapter_ref_id.should_change
                and new_chapter_ref_id != habit.chapter_ref_id
            )
            goal_changing = (
                args.goal_ref_id.should_change and new_goal_ref_id != habit.goal_ref_id
            )

            # Shared writers can keep the owner's life-plan links, but cannot
            # retarget them without writer access to those entities.
            if aspect_changing or chapter_changing or goal_changing:
                aspect = await self.load_entity(
                    uow,
                    context.user.ref_id,
                    Aspect,
                    new_aspect_ref_id,
                )

                if chapter_changing and new_chapter_ref_id is not None:
                    chapter = await self.load_entity(
                        uow, context.user.ref_id, Chapter, new_chapter_ref_id
                    )
                    if chapter.aspect_ref_id != aspect.ref_id:
                        raise InputValidationError(
                            f"Chapter does not belong to aspect '{aspect.name}'"
                        )

                if goal_changing and new_goal_ref_id is not None:
                    goal = await self.load_entity(
                        uow, context.user.ref_id, Goal, new_goal_ref_id
                    )
                    if goal.aspect_ref_id != aspect.ref_id:
                        raise InputValidationError(
                            f"Goal does not belong to aspect '{aspect.name}'"
                        )

        new_stack_ref_id = args.stack_ref_id.or_else(habit.stack_ref_id)
        stack_changing = (
            args.stack_ref_id.should_change and new_stack_ref_id != habit.stack_ref_id
        )
        if stack_changing and new_stack_ref_id is not None:
            stack = await self.load_entity(
                uow, context.user.ref_id, HabitStack, new_stack_ref_id
            )
            if stack.period != habit.gen_params.period:
                raise InputValidationError("Habit period must match the stack period")

        habit_scheduling_params = build_scheduling_params_update(
            habit.scheduling_params,
            args.schedulability,
            args.scheduling_event_duration_mins,
            args.scheduling_event_count,
            args.difficulty.or_else(habit.gen_params.difficulty),
        )

        habit = habit.update(
            ctx=context.domain_context,
            aspect_ref_id=args.aspect_ref_id,
            chapter_ref_id=args.chapter_ref_id,
            goal_ref_id=args.goal_ref_id,
            stack_ref_id=args.stack_ref_id,
            name=args.name,
            is_key=args.is_key,
            gen_params=habit_gen_params,
            scheduling_params=habit_scheduling_params,
            repeats_strategy=args.repeats_strategy,
            repeats_in_period_count=args.repeats_in_period_count,
            suspended=args.suspended,
        )

        habit = await uow.get_for(Habit).save(habit)
        await progress_reporter.mark_updated(habit)

        return HabitUpdateResult(updated_habit=habit)

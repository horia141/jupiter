"""The command for updating a habit."""
from typing import cast

from jupiter.core.domain.concept.habits.habit import Habit
from jupiter.core.domain.concept.habits.habit_name import HabitName
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class HabitUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[HabitName]
    period: UpdateAction[RecurringTaskPeriod]
    eisen: UpdateAction[Eisen | None]
    difficulty: UpdateAction[Difficulty | None]
    actionable_from_day: UpdateAction[RecurringTaskDueAtDay | None]
    actionable_from_month: UpdateAction[RecurringTaskDueAtMonth | None]
    due_at_day: UpdateAction[RecurringTaskDueAtDay | None]
    due_at_month: UpdateAction[RecurringTaskDueAtMonth | None]
    skip_rule: UpdateAction[RecurringTaskSkipRule | None]
    repeats_in_period_count: UpdateAction[int | None]


@mutation_use_case(WorkspaceFeature.HABITS)
class HabitUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[HabitUpdateArgs, None]
):
    """The command for updating a habit."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HabitUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        habit = await uow.get_for(Habit).load_by_id(args.ref_id)

        project = await uow.get_for(Project).load_by_id(habit.project_ref_id)

        need_to_change_inbox_tasks = (
            args.name.should_change
            or args.period.should_change
            or args.eisen.should_change
            or args.difficulty.should_change
            or args.actionable_from_day.should_change
            or args.actionable_from_month.should_change
            or args.due_at_day.should_change
            or args.due_at_month.should_change
            or args.repeats_in_period_count.should_change
        )

        if (
            args.period.should_change
            or args.eisen.should_change
            or args.difficulty.should_change
            or args.actionable_from_day.should_change
            or args.actionable_from_month.should_change
            or args.due_at_day.should_change
            or args.due_at_month.should_change
        ):
            need_to_change_inbox_tasks = True
            habit_gen_params = UpdateAction.change_to(
                RecurringTaskGenParams(
                    args.period.or_else(habit.gen_params.period),
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
                ),
            )
        else:
            habit_gen_params = UpdateAction.do_nothing()

        habit = habit.update(
            ctx=context.domain_context,
            name=args.name,
            gen_params=habit_gen_params,
            skip_rule=args.skip_rule,
            repeats_in_period_count=args.repeats_in_period_count,
        )

        await uow.get_for(Habit).save(habit)
        await progress_reporter.mark_updated(habit)

        if need_to_change_inbox_tasks:
            inbox_task_collection = await uow.get_for(
                InboxTaskCollection
            ).load_by_parent(
                workspace.ref_id,
            )
            all_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                habit_ref_id=[habit.ref_id],
            )

            for inbox_task in all_inbox_tasks:
                schedule = schedules.get_schedule(
                    habit.gen_params.period,
                    habit.name,
                    cast(Timestamp, inbox_task.recurring_gen_right_now),
                    habit.skip_rule,
                    habit.gen_params.actionable_from_day,
                    habit.gen_params.actionable_from_month,
                    habit.gen_params.due_at_day,
                    habit.gen_params.due_at_month,
                )

                inbox_task = inbox_task.update_link_to_habit(
                    ctx=context.domain_context,
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    timeline=schedule.timeline,
                    repeat_index=inbox_task.recurring_repeat_index,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_date,
                    eisen=habit.gen_params.eisen,
                    difficulty=habit.gen_params.difficulty,
                )

                await uow.get_for(InboxTask).save(inbox_task)
                await progress_reporter.mark_updated(inbox_task)

"""The command for updating a habit."""
from dataclasses import dataclass
from typing import Iterable, Optional, cast

from jupiter.core.domain import schedules
from jupiter.core.domain.difficulty import Difficulty
from jupiter.core.domain.eisen import Eisen
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.habits.habit_name import HabitName
from jupiter.core.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class HabitUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[HabitName]
    period: UpdateAction[RecurringTaskPeriod]
    eisen: UpdateAction[Optional[Eisen]]
    difficulty: UpdateAction[Optional[Difficulty]]
    actionable_from_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
    actionable_from_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
    due_at_time: UpdateAction[Optional[RecurringTaskDueAtTime]]
    due_at_day: UpdateAction[Optional[RecurringTaskDueAtDay]]
    due_at_month: UpdateAction[Optional[RecurringTaskDueAtMonth]]
    skip_rule: UpdateAction[Optional[RecurringTaskSkipRule]]
    repeats_in_period_count: UpdateAction[Optional[int]]


class HabitUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[HabitUpdateArgs, None]
):
    """The command for updating a habit."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.HABITS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: HabitUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace

        habit = await uow.habit_repository.load_by_id(args.ref_id)

        project = await uow.project_repository.load_by_id(habit.project_ref_id)

        need_to_change_inbox_tasks = (
            args.name.should_change
            or args.period.should_change
            or args.eisen.should_change
            or args.difficulty.should_change
            or args.actionable_from_day.should_change
            or args.actionable_from_month.should_change
            or args.due_at_time.should_change
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
            or args.due_at_time.should_change
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
                    args.due_at_time.or_else(habit.gen_params.due_at_time),
                    args.due_at_day.or_else(habit.gen_params.due_at_day),
                    args.due_at_month.or_else(habit.gen_params.due_at_month),
                ),
            )
        else:
            habit_gen_params = UpdateAction.do_nothing()

        habit = habit.update(
            name=args.name,
            gen_params=habit_gen_params,
            skip_rule=args.skip_rule,
            repeats_in_period_count=args.repeats_in_period_count,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )

        await uow.habit_repository.save(habit)
        await progress_reporter.mark_updated(habit)

        if need_to_change_inbox_tasks:
            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            all_inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_habit_ref_ids=[habit.ref_id],
            )

            for inbox_task in all_inbox_tasks:
                schedule = schedules.get_schedule(
                    habit.gen_params.period,
                    habit.name,
                    cast(Timestamp, inbox_task.recurring_gen_right_now),
                    user.timezone,
                    habit.skip_rule,
                    habit.gen_params.actionable_from_day,
                    habit.gen_params.actionable_from_month,
                    habit.gen_params.due_at_time,
                    habit.gen_params.due_at_day,
                    habit.gen_params.due_at_month,
                )

                inbox_task = inbox_task.update_link_to_habit(
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    timeline=schedule.timeline,
                    repeat_index=inbox_task.recurring_repeat_index,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_time,
                    eisen=habit.gen_params.eisen,
                    difficulty=habit.gen_params.difficulty,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )

                await uow.inbox_task_repository.save(inbox_task)
                await progress_reporter.mark_updated(inbox_task)

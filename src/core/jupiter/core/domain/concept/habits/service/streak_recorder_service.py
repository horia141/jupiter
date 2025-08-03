"""A service for recording streak marks."""

from typing import Iterable, cast

from jupiter.core.domain.concept.habits.habit import Habit
from jupiter.core.domain.concept.habits.habit_streak_mark import (
    HabitStreakMark,
    HabitStreakMarkRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.context import DomainContext


class HabitStreakRecorderService:
    """A service for recording streak marks."""

    async def upsert(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        today: ADate,
        habit: Habit,
        inbox_tasks: Iterable[InboxTask],
    ) -> None:
        """Record a streak mark."""
        schedule = schedules.get_schedule(
            period=habit.gen_params.period,
            name=habit.name,
            right_now=today.to_timestamp_at_start_of_day(),
        )

        statuses = {inbox_task.ref_id: inbox_task.status for inbox_task in inbox_tasks}

        start_date = schedule.first_day
        while start_date <= schedule.end_day:
            habit_streak_mark = HabitStreakMark.new_mark(
                ctx=ctx,
                habit_ref_id=habit.ref_id,
                date=start_date,
                statuses=statuses,
            )
            await uow.get(HabitStreakMarkRepository).upsert(habit_streak_mark)
            start_date = start_date.add_days(1)

    async def update_with_status(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        habit: Habit,
        inbox_task: InboxTask,
    ) -> None:
        """Update a streak mark with a new status."""
        schedule = schedules.get_schedule(
            period=habit.gen_params.period,
            name=habit.name,
            right_now=cast(Timestamp, inbox_task.recurring_gen_right_now),
        )

        start_date = schedule.first_day
        while start_date <= schedule.end_day:
            habit_streak_mark = await uow.get(
                HabitStreakMarkRepository
            ).load_by_key_optional((habit.ref_id, start_date))
            if habit_streak_mark is None:
                habit_streak_mark = HabitStreakMark.new_mark(
                    ctx=ctx,
                    habit_ref_id=habit.ref_id,
                    date=start_date,
                    statuses={inbox_task.ref_id: inbox_task.status},
                )
            else:
                habit_streak_mark = habit_streak_mark.update_status(
                    ctx, inbox_task.ref_id, inbox_task.status
                )

            await uow.get(HabitStreakMarkRepository).upsert(habit_streak_mark)
            start_date = start_date.add_days(1)

    async def remove_with_status(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        habit: Habit,
        inbox_task: InboxTask,
    ) -> None:
        """Remove a streak mark."""
        schedule = schedules.get_schedule(
            period=habit.gen_params.period,
            name=habit.name,
            right_now=cast(Timestamp, inbox_task.recurring_gen_right_now),
        )

        start_date = schedule.first_day
        while start_date <= schedule.end_day:
            habit_streak_mark = await uow.get(
                HabitStreakMarkRepository
            ).load_by_key_optional((habit.ref_id, start_date))
            if habit_streak_mark is None:
                continue
            else:
                habit_streak_mark = habit_streak_mark.remove_status(
                    ctx, inbox_task.ref_id
                )

            await uow.get(HabitStreakMarkRepository).upsert(habit_streak_mark)
            start_date = start_date.add_days(1)

    async def remove_all(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        habit: Habit,
        today: ADate,
        alternative_period: RecurringTaskPeriod,
    ) -> None:
        """Remove all streak marks."""
        schedule = schedules.get_schedule(
            period=alternative_period,
            name=habit.name,
            right_now=today.to_timestamp_at_start_of_day(),
        )

        start_date = schedule.first_day
        while start_date <= schedule.end_day:
            await uow.get(HabitStreakMarkRepository).remove((habit.ref_id, start_date))
            start_date = start_date.add_days(1)

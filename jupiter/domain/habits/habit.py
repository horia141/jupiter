"""A habit."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.habits.habit_name import HabitName
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.framework.entity import Entity, FIRST_VERSION
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.errors import InputValidationError
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class Habit(Entity):
    """A habit."""

    @dataclass(frozen=True)
    class Created(Entity.Created):
        """Created event."""

    @dataclass(frozen=True)
    class ChangeProject(Entity.Updated):
        """Changed the project event."""

    @dataclass(frozen=True)
    class Updated(Entity.Updated):
        """Updated event."""

    @dataclass(frozen=True)
    class Suspended(Entity.Updated):
        """Suspended event."""

    @dataclass(frozen=True)
    class Unsuspended(Entity.Updated):
        """Unsuspend event."""

    habit_collection_ref_id: EntityId
    project_ref_id: EntityId
    name: HabitName
    gen_params: RecurringTaskGenParams
    skip_rule: Optional[RecurringTaskSkipRule]
    suspended: bool
    repeats_in_period_count: Optional[int]

    @staticmethod
    def new_habit(
            habit_collection_ref_id: EntityId, archived: bool, project_ref_id: EntityId, name: HabitName,
            gen_params: RecurringTaskGenParams, skip_rule: Optional[RecurringTaskSkipRule],
            repeats_in_period_count: Optional[int], suspended: bool,source: EventSource,
            created_time: Timestamp) -> 'Habit':
        """Create a habit."""
        Habit._check_actionable_and_due_date_configs(
            gen_params.actionable_from_day, gen_params.actionable_from_month,
            gen_params.due_at_day, gen_params.due_at_month)
        if repeats_in_period_count is not None:
            if gen_params.period == RecurringTaskPeriod.DAILY:
                raise InputValidationError("Repeats for daily habits are not allowed")
            if repeats_in_period_count < 2:
                raise InputValidationError("Repeats in period needs to be strictly greater than 1 if specified")

        habit = Habit(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=archived,
            created_time=created_time,
            archived_time=created_time if archived else None,
            last_modified_time=created_time,
            events=[Habit.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            habit_collection_ref_id=habit_collection_ref_id,
            project_ref_id=project_ref_id,
            name=name,
            gen_params=gen_params,
            skip_rule=skip_rule,
            repeats_in_period_count=repeats_in_period_count,
            suspended=suspended)
        return habit

    def change_project(
            self, project_ref_id: EntityId, source: EventSource, modification_time: Timestamp) -> 'Habit':
        """Change the project for the habit task."""
        if self.project_ref_id == project_ref_id:
            return self
        return self._new_version(
            project_ref_id=project_ref_id,
            new_event=Habit.ChangeProject.make_event_from_frame_args(source, self.version, modification_time))

    def update(
            self, name: UpdateAction[HabitName], gen_params: UpdateAction[RecurringTaskGenParams],
            skip_rule: UpdateAction[Optional[RecurringTaskSkipRule]],
            repeats_in_period_count: UpdateAction[Optional[int]], source: EventSource,
            modification_time: Timestamp) -> 'Habit':
        """Update the habit."""
        if gen_params.should_change:
            Habit._check_actionable_and_due_date_configs(
                gen_params.value.actionable_from_day, gen_params.value.actionable_from_month,
                gen_params.value.due_at_day, gen_params.value.due_at_month)
            the_gen_params = gen_params.value
        else:
            the_gen_params = self.gen_params

        if repeats_in_period_count.should_change and repeats_in_period_count.value is not None:
            if the_gen_params.period == RecurringTaskPeriod.DAILY:
                raise InputValidationError("Repeats for daily habits are not allowed")
            if repeats_in_period_count.value < 2:
                raise InputValidationError("Repeats in period needs to be strictly greater than 1 if specified")

        return self._new_version(
            name=name.or_else(self.name),
            gen_params=the_gen_params,
            skip_rule=skip_rule.or_else(self.skip_rule),
            repeats_in_period_count=repeats_in_period_count.or_else(self.repeats_in_period_count),
            new_event=Habit.Updated.make_event_from_frame_args(source, self.version, modification_time))

    def suspend(self, source: EventSource, modification_time: Timestamp) -> 'Habit':
        """Suspend the habit."""
        if self.suspended:
            return self
        return self._new_version(
            suspended=True,
            new_event=Habit.Suspended.make_event_from_frame_args(source, self.version, modification_time))

    def unsuspend(self, source: EventSource, modification_time: Timestamp) -> 'Habit':
        """Unsuspend the habit."""
        if self.suspended:
            return self
        return self._new_version(
            suspended=False,
            new_event=Habit.Unsuspended.make_event_from_frame_args(source, self.version, modification_time))


    @staticmethod
    def _check_actionable_and_due_date_configs(
            actionable_from_day: Optional[RecurringTaskDueAtDay],
            actionable_from_month: Optional[RecurringTaskDueAtMonth], due_at_day: Optional[RecurringTaskDueAtDay],
            due_at_month: Optional[RecurringTaskDueAtMonth]) -> None:
        actionable_from_day = actionable_from_day or RecurringTaskDueAtDay(0)
        actionable_from_month = actionable_from_month or RecurringTaskDueAtMonth(0)
        due_at_day = due_at_day or RecurringTaskDueAtDay(1000)
        due_at_month = due_at_month or RecurringTaskDueAtMonth(1000)
        if actionable_from_month.as_int() > due_at_month.as_int():
            raise InputValidationError(
                f"Actionable month {actionable_from_month} should be before due month {due_at_month}")
        if actionable_from_month == due_at_month and actionable_from_day.as_int() > due_at_day.as_int():
            raise InputValidationError(
                f"Actionable day {actionable_from_day} should be before due day {due_at_day}")

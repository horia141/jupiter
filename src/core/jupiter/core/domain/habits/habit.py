"""A habit."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.habits.habit_name import HabitName
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, LeafEntity
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class Habit(LeafEntity):
    """A habit."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class ChangeProject(Entity.Updated):
        """Changed the project event."""

    @dataclass
    class Updated(Entity.Updated):
        """Updated event."""

    @dataclass
    class Suspended(Entity.Updated):
        """Suspended event."""

    @dataclass
    class Unsuspended(Entity.Updated):
        """Unsuspend event."""

    habit_collection_ref_id: EntityId
    project_ref_id: EntityId
    name: HabitName
    gen_params: RecurringTaskGenParams
    skip_rule: Optional[RecurringTaskSkipRule] = None
    suspended: bool = False
    repeats_in_period_count: Optional[int] = None

    @staticmethod
    def new_habit(
        habit_collection_ref_id: EntityId,
        archived: bool,
        project_ref_id: EntityId,
        name: HabitName,
        gen_params: RecurringTaskGenParams,
        skip_rule: Optional[RecurringTaskSkipRule],
        repeats_in_period_count: Optional[int],
        suspended: bool,
        source: EventSource,
        created_time: Timestamp,
    ) -> "Habit":
        """Create a habit."""
        Habit._check_actionable_and_due_date_configs(
            gen_params.actionable_from_day,
            gen_params.actionable_from_month,
            gen_params.due_at_day,
            gen_params.due_at_month,
        )
        if repeats_in_period_count is not None:
            if gen_params.period == RecurringTaskPeriod.DAILY:
                raise InputValidationError("Repeats for daily habits are not allowed")
            if repeats_in_period_count < 2:
                raise InputValidationError(
                    "Repeats in period needs to be strictly greater than 1 if specified",
                )

        habit = Habit(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=archived,
            created_time=created_time,
            archived_time=created_time if archived else None,
            last_modified_time=created_time,
            events=[
                Habit.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            habit_collection_ref_id=habit_collection_ref_id,
            project_ref_id=project_ref_id,
            name=name,
            gen_params=gen_params,
            skip_rule=skip_rule,
            repeats_in_period_count=repeats_in_period_count,
            suspended=suspended,
        )
        return habit

    def change_project(
        self,
        project_ref_id: EntityId,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Habit":
        """Change the project for the habit task."""
        if self.project_ref_id == project_ref_id:
            return self
        return self._new_version(
            project_ref_id=project_ref_id,
            new_event=Habit.ChangeProject.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    def update(
        self,
        name: UpdateAction[HabitName],
        gen_params: UpdateAction[RecurringTaskGenParams],
        skip_rule: UpdateAction[Optional[RecurringTaskSkipRule]],
        repeats_in_period_count: UpdateAction[Optional[int]],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Habit":
        """Update the habit."""
        if gen_params.should_change:
            Habit._check_actionable_and_due_date_configs(
                gen_params.just_the_value.actionable_from_day,
                gen_params.just_the_value.actionable_from_month,
                gen_params.just_the_value.due_at_day,
                gen_params.just_the_value.due_at_month,
            )
            the_gen_params = gen_params.just_the_value
        else:
            the_gen_params = self.gen_params

        if (
            repeats_in_period_count.should_change
            and repeats_in_period_count.just_the_value is not None
        ):
            if the_gen_params.period == RecurringTaskPeriod.DAILY:
                raise InputValidationError("Repeats for daily habits are not allowed")
            if repeats_in_period_count.just_the_value < 2:
                raise InputValidationError(
                    "Repeats in period needs to be strictly greater than 1 if specified",
                )

        return self._new_version(
            name=name.or_else(self.name),
            gen_params=the_gen_params,
            skip_rule=skip_rule.or_else(self.skip_rule),
            repeats_in_period_count=repeats_in_period_count.or_else(
                self.repeats_in_period_count,
            ),
            new_event=Habit.Updated.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    def suspend(self, source: EventSource, modification_time: Timestamp) -> "Habit":
        """Suspend the habit."""
        if self.suspended:
            return self
        return self._new_version(
            suspended=True,
            new_event=Habit.Suspended.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    def unsuspend(self, source: EventSource, modification_time: Timestamp) -> "Habit":
        """Unsuspend the habit."""
        if not self.suspended:
            return self
        return self._new_version(
            suspended=False,
            new_event=Habit.Unsuspended.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    @staticmethod
    def _check_actionable_and_due_date_configs(
        actionable_from_day: Optional[RecurringTaskDueAtDay],
        actionable_from_month: Optional[RecurringTaskDueAtMonth],
        due_at_day: Optional[RecurringTaskDueAtDay],
        due_at_month: Optional[RecurringTaskDueAtMonth],
    ) -> None:
        actionable_from_day = actionable_from_day or RecurringTaskDueAtDay(1)
        actionable_from_month = actionable_from_month or RecurringTaskDueAtMonth(1)
        due_at_day = due_at_day or RecurringTaskDueAtDay(31)
        due_at_month = due_at_month or RecurringTaskDueAtMonth(12)
        if actionable_from_month.as_int() > due_at_month.as_int():
            raise InputValidationError(
                f"Actionable month {actionable_from_month} should be before due month {due_at_month}",
            )
        if (
            actionable_from_month == due_at_month
            and actionable_from_day.as_int() > due_at_day.as_int()
        ):
            raise InputValidationError(
                f"Actionable day {actionable_from_day} should be before due day {due_at_day}",
            )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.habit_collection_ref_id

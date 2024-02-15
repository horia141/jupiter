"""A habit."""
from typing import Optional

from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.habits.habit_name import HabitName
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsRefId,
    LeafEntity,
    OwnsMany,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.update_action import UpdateAction


@entity
class Habit(LeafEntity):
    """A habit."""

    habit_collection: ParentLink
    project_ref_id: EntityId
    name: HabitName
    gen_params: RecurringTaskGenParams
    skip_rule: Optional[RecurringTaskSkipRule] = None
    suspended: bool = False
    repeats_in_period_count: Optional[int] = None

    inbox_tasks = OwnsMany(
        InboxTask, source=InboxTaskSource.HABIT, habit_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_habit(
        ctx: DomainContext,
        habit_collection_ref_id: EntityId,
        project_ref_id: EntityId,
        name: HabitName,
        gen_params: RecurringTaskGenParams,
        skip_rule: Optional[RecurringTaskSkipRule],
        repeats_in_period_count: Optional[int],
        suspended: bool,
    ) -> "Habit":
        """Create a habit."""
        Habit._check_actionable_and_due_date_configs(
            gen_params.period,
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

        return Habit._create(
            ctx,
            habit_collection=ParentLink(habit_collection_ref_id),
            project_ref_id=project_ref_id,
            name=name,
            gen_params=gen_params,
            skip_rule=skip_rule,
            repeats_in_period_count=repeats_in_period_count,
            suspended=suspended,
        )

    @update_entity_action
    def change_project(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
    ) -> "Habit":
        """Change the project for the habit task."""
        if self.project_ref_id == project_ref_id:
            return self
        return self._new_version(
            ctx,
            project_ref_id=project_ref_id,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[HabitName],
        gen_params: UpdateAction[RecurringTaskGenParams],
        skip_rule: UpdateAction[Optional[RecurringTaskSkipRule]],
        repeats_in_period_count: UpdateAction[Optional[int]],
    ) -> "Habit":
        """Update the habit."""
        if gen_params.should_change:
            Habit._check_actionable_and_due_date_configs(
                gen_params.just_the_value.period,
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
            ctx,
            name=name.or_else(self.name),
            gen_params=the_gen_params,
            skip_rule=skip_rule.or_else(self.skip_rule),
            repeats_in_period_count=repeats_in_period_count.or_else(
                self.repeats_in_period_count,
            ),
        )

    @update_entity_action
    def suspend(self, ctx: DomainContext) -> "Habit":
        """Suspend the habit."""
        if self.suspended:
            return self
        return self._new_version(
            ctx,
            suspended=True,
        )

    @update_entity_action
    def unsuspend(self, ctx: DomainContext) -> "Habit":
        """Unsuspend the habit."""
        if not self.suspended:
            return self
        return self._new_version(
            ctx,
            suspended=False,
        )

    @staticmethod
    def _check_actionable_and_due_date_configs(
        period: RecurringTaskPeriod,
        actionable_from_day: Optional[RecurringTaskDueAtDay],
        actionable_from_month: Optional[RecurringTaskDueAtMonth],
        due_at_day: Optional[RecurringTaskDueAtDay],
        due_at_month: Optional[RecurringTaskDueAtMonth],
    ) -> None:
        actionable_from_day = actionable_from_day or RecurringTaskDueAtDay.first_of(
            period
        )
        actionable_from_month = (
            actionable_from_month or RecurringTaskDueAtMonth.first_of(period)
        )
        due_at_day = due_at_day or RecurringTaskDueAtDay.end_of(period)
        due_at_month = due_at_month or RecurringTaskDueAtMonth.end_of(period)
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

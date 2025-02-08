"""Shared domain objects."""
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import CompositeValue, value


@value
class RecurringTaskGenParams(CompositeValue):
    """Parameters for metric collection."""

    period: RecurringTaskPeriod
    eisen: Eisen
    difficulty: Difficulty
    actionable_from_day: RecurringTaskDueAtDay | None
    actionable_from_month: RecurringTaskDueAtMonth | None
    due_at_day: RecurringTaskDueAtDay | None
    due_at_month: RecurringTaskDueAtMonth | None
    skip_rule: RecurringTaskSkipRule | None

    def _validate(self) -> None:
        the_actionable_from_day = (
            self.actionable_from_day or RecurringTaskDueAtDay.first_of(self.period)
        )
        the_due_at_day = self.due_at_day or RecurringTaskDueAtDay.end_of(self.period)
        if (
            self.period is RecurringTaskPeriod.DAILY
            or self.period is RecurringTaskPeriod.WEEKLY
            or self.period is RecurringTaskPeriod.MONTHLY
        ):
            if the_actionable_from_day.as_int() > the_due_at_day.as_int():
                raise InputValidationError(
                    f"Actionable day {the_actionable_from_day} should be before due day {the_due_at_day}",
                )
        the_actionable_from_month = (
            self.actionable_from_month or RecurringTaskDueAtMonth.first_of(self.period)
        )
        the_due_at_month = self.due_at_month or RecurringTaskDueAtMonth.end_of(
            self.period
        )
        if the_actionable_from_month.as_int() > the_due_at_month.as_int():
            raise InputValidationError(
                f"Actionable month {the_actionable_from_month} should be before due month {the_due_at_month}",
            )
        if (
            the_actionable_from_month == the_due_at_month
            and the_actionable_from_day.as_int() > the_due_at_day.as_int()
        ):
            raise InputValidationError(
                f"Actionable day {the_actionable_from_day} should be before due day {the_due_at_day}",
            )

        if self.skip_rule is not None:
            if not self.skip_rule.is_compatible_with(self.period):
                raise InputValidationError(
                    f"Skip rule {self.skip_rule} is not compatible with period {self.period}",
                )

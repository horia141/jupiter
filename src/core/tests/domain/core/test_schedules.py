"""Tests for schedules."""

import pendulum
import pytest
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.core.schedules import Schedule, get_schedule
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.base.timestamp import Timestamp


@pytest.fixture()
def right_now() -> Timestamp:
    return Timestamp.from_date_and_time(pendulum.datetime(2023, 12, 19, 10, 14))


def test_get_schedule_daily_simple(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.DAILY,
        name=EntityName("A task"),
        right_now=right_now,
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.DAILY
    assert schedule.first_day == ADate.from_str("2023-12-19")
    assert schedule.end_day == ADate.from_str("2023-12-19")
    assert schedule.timeline == "2023,Q4,Dec,W51,D2"
    assert schedule.actionable_date is None
    assert schedule.due_date == ADate.from_str("2023-12-19")
    assert schedule.full_name == InboxTaskName("A task 23:Dec19")


def test_get_schedule_daily_with_skip_rule(right_now: Timestamp) -> None:
    schedule_even = get_schedule(
        period=RecurringTaskPeriod.DAILY,
        name=EntityName("A task"),
        right_now=right_now,
        skip_rule=RecurringTaskSkipRule("even"),
    )

    assert isinstance(schedule_even, Schedule)
    assert schedule_even.should_skip is True

    schedule_odd = get_schedule(
        period=RecurringTaskPeriod.DAILY,
        name=EntityName("A task"),
        right_now=right_now,
        skip_rule=RecurringTaskSkipRule("odd"),
    )

    assert isinstance(schedule_odd, Schedule)
    assert schedule_odd.should_skip is False


def test_get_schedule_weekly_simple(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.WEEKLY,
        name=EntityName("A task"),
        right_now=right_now,
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.WEEKLY
    assert schedule.first_day == ADate.from_str("2023-12-18")
    assert schedule.end_day == ADate.from_str("2023-12-24")
    assert schedule.timeline == "2023,Q4,Dec,W51"
    assert schedule.actionable_date is None
    assert schedule.due_date == ADate.from_str("2023-12-24")
    assert schedule.full_name == InboxTaskName("A task 23:W51")


def test_get_schedule_weekly_with_skip_rule(right_now: Timestamp) -> None:
    schedule_even = get_schedule(
        period=RecurringTaskPeriod.WEEKLY,
        name=EntityName("A task"),
        right_now=right_now,
        skip_rule=RecurringTaskSkipRule("even"),
    )

    assert isinstance(schedule_even, Schedule)
    assert schedule_even.should_skip is False

    schedule_odd = get_schedule(
        period=RecurringTaskPeriod.WEEKLY,
        name=EntityName("A task"),
        right_now=right_now,
        skip_rule=RecurringTaskSkipRule("odd"),
    )

    assert isinstance(schedule_odd, Schedule)
    assert schedule_odd.should_skip is True


def test_get_schedule_weekly_set_actionable_from_day(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.WEEKLY,
        name=EntityName("A task"),
        right_now=right_now,
        actionable_from_day=RecurringTaskDueAtDay(RecurringTaskPeriod.WEEKLY, 3),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.WEEKLY
    assert schedule.first_day == ADate.from_str("2023-12-18")
    assert schedule.end_day == ADate.from_str("2023-12-24")
    assert schedule.timeline == "2023,Q4,Dec,W51"
    assert schedule.actionable_date == ADate.from_str("2023-12-20")
    assert schedule.due_date == ADate.from_str("2023-12-24")
    assert schedule.full_name == InboxTaskName("A task 23:W51")


def test_get_schedule_weekly_set_due_at_day(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.WEEKLY,
        name=EntityName("A task"),
        right_now=right_now,
        due_at_day=RecurringTaskDueAtDay(RecurringTaskPeriod.WEEKLY, 3),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.WEEKLY
    assert schedule.first_day == ADate.from_str("2023-12-18")
    assert schedule.end_day == ADate.from_str("2023-12-24")
    assert schedule.timeline == "2023,Q4,Dec,W51"
    assert schedule.actionable_date is None
    assert schedule.due_date == ADate.from_str("2023-12-20")
    assert schedule.full_name == InboxTaskName("A task 23:W51")


def test_get_schedule_weekly_set_actionable_from_day_and_due_at_day(
    right_now: Timestamp,
) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.WEEKLY,
        name=EntityName("A task"),
        right_now=right_now,
        actionable_from_day=RecurringTaskDueAtDay(RecurringTaskPeriod.WEEKLY, 3),
        due_at_day=RecurringTaskDueAtDay(RecurringTaskPeriod.WEEKLY, 5),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.WEEKLY
    assert schedule.first_day == ADate.from_str("2023-12-18")
    assert schedule.end_day == ADate.from_str("2023-12-24")
    assert schedule.timeline == "2023,Q4,Dec,W51"
    assert schedule.actionable_date == ADate.from_str("2023-12-20")
    assert schedule.due_date == ADate.from_str("2023-12-22")
    assert schedule.full_name == InboxTaskName("A task 23:W51")


def test_get_schedule_monthly_simple(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.MONTHLY,
        name=EntityName("A task"),
        right_now=right_now,
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.MONTHLY
    assert schedule.first_day == ADate.from_str("2023-12-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023,Q4,Dec"
    assert schedule.actionable_date is None
    assert schedule.due_date == ADate.from_str("2023-12-31")
    assert schedule.full_name == InboxTaskName("A task 23:Dec")


def test_get_sechdule_monthly_with_skip_rule(right_now: Timestamp) -> None:
    schedule_even = get_schedule(
        period=RecurringTaskPeriod.MONTHLY,
        name=EntityName("A task"),
        right_now=right_now,
        skip_rule=RecurringTaskSkipRule("even"),
    )

    assert isinstance(schedule_even, Schedule)
    assert schedule_even.should_skip is True

    schedule_odd = get_schedule(
        period=RecurringTaskPeriod.MONTHLY,
        name=EntityName("A task"),
        right_now=right_now,
        skip_rule=RecurringTaskSkipRule("odd"),
    )

    assert isinstance(schedule_odd, Schedule)
    assert schedule_odd.should_skip is False


def test_get_schedule_monthly_set_actionable_from_day(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.MONTHLY,
        name=EntityName("A task"),
        right_now=right_now,
        actionable_from_day=RecurringTaskDueAtDay(RecurringTaskPeriod.MONTHLY, 15),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.MONTHLY
    assert schedule.first_day == ADate.from_str("2023-12-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023,Q4,Dec"
    assert schedule.actionable_date == ADate.from_str("2023-12-15")
    assert schedule.due_date == ADate.from_str("2023-12-31")
    assert schedule.full_name == InboxTaskName("A task 23:Dec")


def test_get_schedule_monthly_set_due_at_day(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.MONTHLY,
        name=EntityName("A task"),
        right_now=right_now,
        due_at_day=RecurringTaskDueAtDay(RecurringTaskPeriod.MONTHLY, 15),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.MONTHLY
    assert schedule.first_day == ADate.from_str("2023-12-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023,Q4,Dec"
    assert schedule.actionable_date is None
    assert schedule.due_date == ADate.from_str("2023-12-15")
    assert schedule.full_name == InboxTaskName("A task 23:Dec")


def test_get_schedule_monthly_set_actionable_from_day_and_due_at_day(
    right_now: Timestamp,
) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.MONTHLY,
        name=EntityName("A task"),
        right_now=right_now,
        actionable_from_day=RecurringTaskDueAtDay(RecurringTaskPeriod.MONTHLY, 15),
        due_at_day=RecurringTaskDueAtDay(RecurringTaskPeriod.MONTHLY, 20),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.MONTHLY
    assert schedule.first_day == ADate.from_str("2023-12-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023,Q4,Dec"
    assert schedule.actionable_date == ADate.from_str("2023-12-15")
    assert schedule.due_date == ADate.from_str("2023-12-20")
    assert schedule.full_name == InboxTaskName("A task 23:Dec")


def test_get_schedule_quarterly_simple(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.QUARTERLY,
        name=EntityName("A task"),
        right_now=right_now,
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.QUARTERLY
    assert schedule.first_day == ADate.from_str("2023-10-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023,Q4"
    assert schedule.actionable_date is None
    assert schedule.due_date == ADate.from_str("2023-12-31")
    assert schedule.full_name == InboxTaskName("A task 23:Q4")


def test_get_schedule_quarterly_with_skip_rule(right_now: Timestamp) -> None:
    schedule_even = get_schedule(
        period=RecurringTaskPeriod.QUARTERLY,
        name=EntityName("A task"),
        right_now=right_now,
        skip_rule=RecurringTaskSkipRule("even"),
    )

    assert isinstance(schedule_even, Schedule)
    assert schedule_even.should_skip is True

    schedule_odd = get_schedule(
        period=RecurringTaskPeriod.QUARTERLY,
        name=EntityName("A task"),
        right_now=right_now,
        skip_rule=RecurringTaskSkipRule("odd"),
    )

    assert isinstance(schedule_odd, Schedule)
    assert schedule_odd.should_skip is False


def test_get_schedule_quarterly_set_actionable_from_day(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.QUARTERLY,
        name=EntityName("A task"),
        right_now=right_now,
        actionable_from_day=RecurringTaskDueAtDay(RecurringTaskPeriod.QUARTERLY, 15),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.QUARTERLY
    assert schedule.first_day == ADate.from_str("2023-10-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023,Q4"
    assert schedule.actionable_date == ADate.from_str("2023-10-15")
    assert schedule.due_date == ADate.from_str("2023-12-31")
    assert schedule.full_name == InboxTaskName("A task 23:Q4")


def test_get_schedule_quarterly_set_actionable_from_month(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.QUARTERLY,
        name=EntityName("A task"),
        right_now=right_now,
        actionable_from_month=RecurringTaskDueAtMonth(RecurringTaskPeriod.QUARTERLY, 2),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.QUARTERLY
    assert schedule.first_day == ADate.from_str("2023-10-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023,Q4"
    assert schedule.actionable_date == ADate.from_str("2023-11-01")
    assert schedule.due_date == ADate.from_str("2023-12-31")
    assert schedule.full_name == InboxTaskName("A task 23:Q4")


def test_get_schedule_quarterly_set_actionable_from_day_and_month(
    right_now: Timestamp,
) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.QUARTERLY,
        name=EntityName("A task"),
        right_now=right_now,
        actionable_from_day=RecurringTaskDueAtDay(RecurringTaskPeriod.QUARTERLY, 15),
        actionable_from_month=RecurringTaskDueAtMonth(RecurringTaskPeriod.QUARTERLY, 2),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.QUARTERLY
    assert schedule.first_day == ADate.from_str("2023-10-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023,Q4"
    assert schedule.actionable_date == ADate.from_str("2023-11-15")
    assert schedule.due_date == ADate.from_str("2023-12-31")
    assert schedule.full_name == InboxTaskName("A task 23:Q4")


def test_get_schedule_quarterly_set_due_at_day(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.QUARTERLY,
        name=EntityName("A task"),
        right_now=right_now,
        due_at_day=RecurringTaskDueAtDay(RecurringTaskPeriod.QUARTERLY, 15),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.QUARTERLY
    assert schedule.first_day == ADate.from_str("2023-10-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023,Q4"
    assert schedule.actionable_date is None
    assert schedule.due_date == ADate.from_str("2023-10-15")
    assert schedule.full_name == InboxTaskName("A task 23:Q4")


def test_get_schedule_quarterly_set_due_at_month(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.QUARTERLY,
        name=EntityName("A task"),
        right_now=right_now,
        due_at_month=RecurringTaskDueAtMonth(RecurringTaskPeriod.QUARTERLY, 2),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.QUARTERLY
    assert schedule.first_day == ADate.from_str("2023-10-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023,Q4"
    assert schedule.actionable_date is None
    assert schedule.due_date == ADate.from_str("2023-11-30")
    assert schedule.full_name == InboxTaskName("A task 23:Q4")


def test_get_schedule_quarterly_set_due_at_day_and_month(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.QUARTERLY,
        name=EntityName("A task"),
        right_now=right_now,
        due_at_day=RecurringTaskDueAtDay(RecurringTaskPeriod.QUARTERLY, 15),
        due_at_month=RecurringTaskDueAtMonth(RecurringTaskPeriod.QUARTERLY, 2),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.QUARTERLY
    assert schedule.first_day == ADate.from_str("2023-10-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023,Q4"
    assert schedule.actionable_date is None
    assert schedule.due_date == ADate.from_str("2023-11-15")
    assert schedule.full_name == InboxTaskName("A task 23:Q4")


def test_get_schedule_quarterly_set_all_actionable_and_due(
    right_now: Timestamp,
) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.QUARTERLY,
        name=EntityName("A task"),
        right_now=right_now,
        actionable_from_day=RecurringTaskDueAtDay(RecurringTaskPeriod.QUARTERLY, 15),
        actionable_from_month=RecurringTaskDueAtMonth(RecurringTaskPeriod.QUARTERLY, 2),
        due_at_day=RecurringTaskDueAtDay(RecurringTaskPeriod.QUARTERLY, 20),
        due_at_month=RecurringTaskDueAtMonth(RecurringTaskPeriod.QUARTERLY, 3),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.QUARTERLY
    assert schedule.first_day == ADate.from_str("2023-10-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023,Q4"
    assert schedule.actionable_date == ADate.from_str("2023-11-15")
    assert schedule.due_date == ADate.from_str("2023-12-20")
    assert schedule.full_name == InboxTaskName("A task 23:Q4")


def test_get_schedule_yearly_simple(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.YEARLY,
        name=EntityName("A task"),
        right_now=right_now,
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.YEARLY
    assert schedule.first_day == ADate.from_str("2023-01-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023"
    assert schedule.actionable_date is None
    assert schedule.due_date == ADate.from_str("2023-12-31")
    assert schedule.full_name == InboxTaskName("A task 23")


def test_get_schedule_yearly_with_skip_rule_does_not_matter(
    right_now: Timestamp,
) -> None:
    schedule_even = get_schedule(
        period=RecurringTaskPeriod.YEARLY,
        name=EntityName("A task"),
        right_now=right_now,
        skip_rule=RecurringTaskSkipRule("even"),
    )

    assert isinstance(schedule_even, Schedule)
    assert schedule_even.should_skip is False

    schedule_odd = get_schedule(
        period=RecurringTaskPeriod.YEARLY,
        name=EntityName("A task"),
        right_now=right_now,
        skip_rule=RecurringTaskSkipRule("odd"),
    )

    assert isinstance(schedule_odd, Schedule)
    assert schedule_odd.should_skip is False


def test_get_schedule_yearly_set_actionable_from_day(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.YEARLY,
        name=EntityName("A task"),
        right_now=right_now,
        actionable_from_day=RecurringTaskDueAtDay(RecurringTaskPeriod.YEARLY, 15),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.YEARLY
    assert schedule.first_day == ADate.from_str("2023-01-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023"
    assert schedule.actionable_date == ADate.from_str("2023-01-15")
    assert schedule.due_date == ADate.from_str("2023-12-31")
    assert schedule.full_name == InboxTaskName("A task 23")


def test_get_schedule_yearly_set_actionable_from_month(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.YEARLY,
        name=EntityName("A task"),
        right_now=right_now,
        actionable_from_month=RecurringTaskDueAtMonth(RecurringTaskPeriod.YEARLY, 4),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.YEARLY
    assert schedule.first_day == ADate.from_str("2023-01-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023"
    assert schedule.actionable_date == ADate.from_str("2023-04-01")
    assert schedule.due_date == ADate.from_str("2023-12-31")
    assert schedule.full_name == InboxTaskName("A task 23")


def test_get_schedule_yearly_set_actionable_from_day_and_month(
    right_now: Timestamp,
) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.YEARLY,
        name=EntityName("A task"),
        right_now=right_now,
        actionable_from_day=RecurringTaskDueAtDay(RecurringTaskPeriod.YEARLY, 15),
        actionable_from_month=RecurringTaskDueAtMonth(RecurringTaskPeriod.YEARLY, 4),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.YEARLY
    assert schedule.first_day == ADate.from_str("2023-01-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023"
    assert schedule.actionable_date == ADate.from_str("2023-04-15")
    assert schedule.due_date == ADate.from_str("2023-12-31")
    assert schedule.full_name == InboxTaskName("A task 23")


def test_get_schedule_yearly_set_due_at_day(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.YEARLY,
        name=EntityName("A task"),
        right_now=right_now,
        due_at_day=RecurringTaskDueAtDay(RecurringTaskPeriod.YEARLY, 15),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.YEARLY
    assert schedule.first_day == ADate.from_str("2023-01-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023"
    assert schedule.actionable_date is None
    assert schedule.due_date == ADate.from_str("2023-01-15")
    assert schedule.full_name == InboxTaskName("A task 23")


def test_get_schedule_yearly_set_due_at_month(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.YEARLY,
        name=EntityName("A task"),
        right_now=right_now,
        due_at_month=RecurringTaskDueAtMonth(RecurringTaskPeriod.YEARLY, 4),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.YEARLY
    assert schedule.first_day == ADate.from_str("2023-01-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023"
    assert schedule.actionable_date is None
    assert schedule.due_date == ADate.from_str("2023-04-30")
    assert schedule.full_name == InboxTaskName("A task 23")


def test_get_schedule_yearly_set_due_at_day_and_month(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.YEARLY,
        name=EntityName("A task"),
        right_now=right_now,
        due_at_day=RecurringTaskDueAtDay(RecurringTaskPeriod.YEARLY, 15),
        due_at_month=RecurringTaskDueAtMonth(RecurringTaskPeriod.YEARLY, 4),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.YEARLY
    assert schedule.first_day == ADate.from_str("2023-01-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023"
    assert schedule.actionable_date is None
    assert schedule.due_date == ADate.from_str("2023-04-15")
    assert schedule.full_name == InboxTaskName("A task 23")


def test_get_schedule_yearly_set_all_actionable_and_due(right_now: Timestamp) -> None:
    """It should return a schedule."""
    # Given a schedule
    schedule = get_schedule(
        period=RecurringTaskPeriod.YEARLY,
        name=EntityName("A task"),
        right_now=right_now,
        actionable_from_day=RecurringTaskDueAtDay(RecurringTaskPeriod.YEARLY, 15),
        actionable_from_month=RecurringTaskDueAtMonth(RecurringTaskPeriod.YEARLY, 4),
        due_at_day=RecurringTaskDueAtDay(RecurringTaskPeriod.YEARLY, 20),
        due_at_month=RecurringTaskDueAtMonth(RecurringTaskPeriod.YEARLY, 5),
    )

    # Then it should return a schedule
    assert isinstance(schedule, Schedule)
    assert schedule.period == RecurringTaskPeriod.YEARLY
    assert schedule.first_day == ADate.from_str("2023-01-01")
    assert schedule.end_day == ADate.from_str("2023-12-31")
    assert schedule.timeline == "2023"
    assert schedule.actionable_date == ADate.from_str("2023-04-15")
    assert schedule.due_date == ADate.from_str("2023-05-20")
    assert schedule.full_name == InboxTaskName("A task 23")


# test for contains timestamp
# test year two digits

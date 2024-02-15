"""Tests for schedules."""

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.schedules import Schedule, get_schedule
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.base.timestamp import Timestamp
import pendulum
from pendulum.datetime import DateTime
from pytest import fixture


@fixture
def right_now() -> Timestamp:
    return Timestamp.from_date_and_time(pendulum.parse("2023-12-19 10:14"))


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


# test for contains timestamp
    # test with generic
    # test for actionable date
    # test for due date
    # test for due date
    # test for skip rule
    # test year two digits
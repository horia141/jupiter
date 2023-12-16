"""Tests for timeline."""
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.timeline import infer_timeline
from jupiter.core.framework.base.timestamp import Timestamp


def test_infer_timeline_for_none_period() -> None:
    period = None
    right_now = Timestamp.from_raw("2021-01-01T00:00:00Z")
    assert infer_timeline(period, right_now) == "Lifetime"


def test_infer_timeline_for_daily_period() -> None:
    period = RecurringTaskPeriod.DAILY
    right_now = Timestamp.from_raw("2021-01-01T00:00:00Z")
    assert infer_timeline(period, right_now) == "2021,Q1,Jan,W53,D5"


def test_every_day_of_the_year_maps_to_a_distinct_daily_timeline() -> None:
    period = RecurringTaskPeriod.DAILY
    initial = Timestamp.from_raw("2021-01-01T00:00:00Z")
    all_timelines = set()
    for day in range(0, 365):
        right_now = Timestamp.from_date_and_time(initial.value.add(days=day))
        all_timelines.add(infer_timeline(period, right_now))

    assert len(all_timelines) == 365


def test_infer_timeline_for_weekly_period() -> None:
    period = RecurringTaskPeriod.WEEKLY
    right_now = Timestamp.from_raw("2021-01-01T00:00:00Z")
    assert infer_timeline(period, right_now) == "2020,Q4,Dec,W53"


def test_every_day_of_the_year_maps_to_one_of_53_weekly_timelines() -> None:
    period = RecurringTaskPeriod.WEEKLY
    initial = Timestamp.from_raw("2021-01-01T00:00:00Z")
    all_timelines = set()
    for day in range(0, 365):
        right_now = Timestamp.from_date_and_time(initial.value.add(days=day))
        all_timelines.add(infer_timeline(period, right_now))

    assert len(all_timelines) == 53


def test_infer_timeline_for_monthly_period() -> None:
    period = RecurringTaskPeriod.MONTHLY
    right_now = Timestamp.from_raw("2021-01-01T00:00:00Z")
    assert infer_timeline(period, right_now) == "2021,Q1,Jan"


def test_every_day_of_the_year_maps_to_one_of_12_monthly_timelines() -> None:
    period = RecurringTaskPeriod.MONTHLY
    initial = Timestamp.from_raw("2021-01-01T00:00:00Z")
    all_timelines = set()
    for day in range(0, 365):
        right_now = Timestamp.from_date_and_time(initial.value.add(days=day))
        all_timelines.add(infer_timeline(period, right_now))

    assert len(all_timelines) == 12


def test_infer_timeline_for_quarterly_period() -> None:
    period = RecurringTaskPeriod.QUARTERLY
    right_now = Timestamp.from_raw("2021-01-01T00:00:00Z")
    assert infer_timeline(period, right_now) == "2021,Q1"


def test_every_day_of_the_year_maps_to_one_of_4_quarterly_timelines() -> None:
    period = RecurringTaskPeriod.QUARTERLY
    initial = Timestamp.from_raw("2021-01-01T00:00:00Z")
    all_timelines = set()
    for day in range(0, 365):
        right_now = Timestamp.from_date_and_time(initial.value.add(days=day))
        all_timelines.add(infer_timeline(period, right_now))

    assert len(all_timelines) == 4


def test_infer_timeline_for_yearly_period() -> None:
    period = RecurringTaskPeriod.YEARLY
    right_now = Timestamp.from_raw("2021-01-01T00:00:00Z")
    assert infer_timeline(period, right_now) == "2021"


def test_every_day_of_the_year_maps_to_one_of_1_yearly_timelines() -> None:
    period = RecurringTaskPeriod.YEARLY
    initial = Timestamp.from_raw("2021-01-01T00:00:00Z")
    all_timelines = set()
    for day in range(0, 365):
        right_now = Timestamp.from_date_and_time(initial.value.add(days=day))
        all_timelines.add(infer_timeline(period, right_now))

    assert len(all_timelines) == 1

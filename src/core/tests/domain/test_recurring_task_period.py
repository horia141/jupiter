"""Tests for recurring task period."""
import pytest
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.errors import InputValidationError


def test_to_nice_string() -> None:
    assert RecurringTaskPeriod.DAILY.to_nice() == "Daily"
    assert RecurringTaskPeriod.WEEKLY.to_nice() == "Weekly"
    assert RecurringTaskPeriod.MONTHLY.to_nice() == "Monthly"
    assert RecurringTaskPeriod.QUARTERLY.to_nice() == "Quarterly"
    assert RecurringTaskPeriod.YEARLY.to_nice() == "Yearly"


def test_from_raw_all_values_for_completeness() -> None:
    assert RecurringTaskPeriod.from_raw("daily") == RecurringTaskPeriod.DAILY
    assert RecurringTaskPeriod.from_raw("weekly") == RecurringTaskPeriod.WEEKLY
    assert RecurringTaskPeriod.from_raw("monthly") == RecurringTaskPeriod.MONTHLY
    assert RecurringTaskPeriod.from_raw("quarterly") == RecurringTaskPeriod.QUARTERLY
    assert RecurringTaskPeriod.from_raw("yearly") == RecurringTaskPeriod.YEARLY


def test_from_raw_with_a_null_value_raises() -> None:
    with pytest.raises(InputValidationError):
        RecurringTaskPeriod.from_raw(None)


def test_from_raw_with_an_empty_value_raises() -> None:
    with pytest.raises(InputValidationError):
        RecurringTaskPeriod.from_raw("")


def test_from_raw_with_a_bad_value_raises() -> None:
    with pytest.raises(InputValidationError):
        RecurringTaskPeriod.from_raw("bad-value")


def test_all_values_for_completeness() -> None:
    assert RecurringTaskPeriod.all_values() == {
        RecurringTaskPeriod.DAILY.value,
        RecurringTaskPeriod.WEEKLY.value,
        RecurringTaskPeriod.MONTHLY.value,
        RecurringTaskPeriod.QUARTERLY.value,
        RecurringTaskPeriod.YEARLY.value,
    }

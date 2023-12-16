"""Tests for recurring task due at time."""
import pytest
from jupiter.core.domain.core.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.framework.errors import InputValidationError


def test_from_raw_parses_a_valid_time() -> None:
    assert RecurringTaskDueAtTime.from_raw("00:00") == RecurringTaskDueAtTime("00:00")


def test_from_raw_null_raises_error() -> None:
    with pytest.raises(InputValidationError):
        RecurringTaskDueAtTime.from_raw(None)

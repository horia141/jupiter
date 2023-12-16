"""Tests for recurring task skip rule."""
import pytest
from jupiter.core.domain.core.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.framework.errors import InputValidationError


def test_from_raw_with_a_valid_value() -> None:
    skip_rule = RecurringTaskSkipRule.from_raw("skip rule")
    assert str(skip_rule) == "skip rule"


def test_from_raw_with_an_empty_value_is_ok() -> None:
    skip_rule = RecurringTaskSkipRule.from_raw(" ")
    assert not str(skip_rule)


def test_from_raw_with_a_null_value() -> None:
    with pytest.raises(InputValidationError):
        RecurringTaskSkipRule.from_raw(None)


def test_str() -> None:
    skip_rule = RecurringTaskSkipRule.from_raw("skip rule")
    assert str(skip_rule) == "skip rule"

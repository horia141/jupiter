"""Tests for sync target."""
import pytest
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.errors import InputValidationError


def test_from_raw_with_all_valid_values() -> None:
    assert SyncTarget.from_raw("inbox-tasks") == SyncTarget.INBOX_TASKS
    assert SyncTarget.from_raw("habits") == SyncTarget.HABITS
    assert SyncTarget.from_raw("chores") == SyncTarget.CHORES
    assert SyncTarget.from_raw("big-plans") == SyncTarget.BIG_PLANS
    assert SyncTarget.from_raw("docs") == SyncTarget.DOCS
    assert SyncTarget.from_raw("vacations") == SyncTarget.VACATIONS
    assert SyncTarget.from_raw("projects") == SyncTarget.PROJECTS
    assert SyncTarget.from_raw("smart-lists") == SyncTarget.SMART_LISTS
    assert SyncTarget.from_raw("metrics") == SyncTarget.METRICS
    assert SyncTarget.from_raw("persons") == SyncTarget.PERSONS
    assert SyncTarget.from_raw("slack-tasks") == SyncTarget.SLACK_TASKS
    assert SyncTarget.from_raw("email-tasks") == SyncTarget.EMAIL_TASKS


def test_from_raw_with_null_raises_error() -> None:
    with pytest.raises(InputValidationError):
        SyncTarget.from_raw(None)


def test_from_raw_with_empty_string_raises_error() -> None:
    with pytest.raises(InputValidationError):
        SyncTarget.from_raw("")


def test_from_raw_with_bad_value_raises_error() -> None:
    with pytest.raises(InputValidationError):
        SyncTarget.from_raw("bad-value")


def test_all_values_for_completeness() -> None:
    assert SyncTarget.all_values() == {
        SyncTarget.INBOX_TASKS.value,
        SyncTarget.HABITS.value,
        SyncTarget.CHORES.value,
        SyncTarget.BIG_PLANS.value,
        SyncTarget.DOCS.value,
        SyncTarget.VACATIONS.value,
        SyncTarget.PROJECTS.value,
        SyncTarget.SMART_LISTS.value,
        SyncTarget.METRICS.value,
        SyncTarget.PERSONS.value,
        SyncTarget.SLACK_TASKS.value,
        SyncTarget.EMAIL_TASKS.value,
    }

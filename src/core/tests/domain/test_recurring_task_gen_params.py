"""Tests for gen parmas."""
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod


def test_construction_with_minimal_params() -> None:
    params = RecurringTaskGenParams(period=RecurringTaskPeriod.DAILY)
    assert params.period == RecurringTaskPeriod.DAILY
    assert params.eisen is None
    assert params.difficulty is None
    assert params.actionable_from_day is None
    assert params.actionable_from_month is None
    assert params.due_at_day is None
    assert params.due_at_month is None

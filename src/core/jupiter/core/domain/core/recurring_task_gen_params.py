"""Shared domain objects."""
from typing import Optional

from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.value import CompositeValue, value


@value
class RecurringTaskGenParams(CompositeValue):
    """Parameters for metric collection."""

    period: RecurringTaskPeriod
    eisen: Optional[Eisen] = None
    difficulty: Optional[Difficulty] = None
    actionable_from_day: Optional[RecurringTaskDueAtDay] = None
    actionable_from_month: Optional[RecurringTaskDueAtMonth] = None
    due_at_day: Optional[RecurringTaskDueAtDay] = None
    due_at_month: Optional[RecurringTaskDueAtMonth] = None

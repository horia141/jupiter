"""Shared domain objects."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_period import RecurringTaskPeriod


@dataclass()
class RecurringTaskGenParams:
    """Parameters for metric collection."""

    period: RecurringTaskPeriod
    eisen: Eisen
    difficulty: Optional[Difficulty]
    actionable_from_day: Optional[RecurringTaskDueAtDay]
    actionable_from_month: Optional[RecurringTaskDueAtMonth]
    due_at_time: Optional[RecurringTaskDueAtTime]
    due_at_day: Optional[RecurringTaskDueAtDay]
    due_at_month: Optional[RecurringTaskDueAtMonth]

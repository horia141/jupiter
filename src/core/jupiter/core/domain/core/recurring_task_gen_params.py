"""Shared domain objects."""

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
    eisen: Eisen | None = None
    difficulty: Difficulty | None = None
    actionable_from_day: RecurringTaskDueAtDay | None = None
    actionable_from_month: RecurringTaskDueAtMonth | None = None
    due_at_day: RecurringTaskDueAtDay | None = None
    due_at_month: RecurringTaskDueAtMonth | None = None

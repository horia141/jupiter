"""The due day for a recurring task."""
from dataclasses import dataclass
from typing import Final, Optional, Dict, Tuple

from domain.common.recurring_task_period import RecurringTaskPeriod
from models.errors import ModelValidationError
from models.frame.value import Value

_RECURRING_TASK_DUE_AT_DAY_BOUNDS: Final[Dict[RecurringTaskPeriod, Tuple[int, int]]] = {
    RecurringTaskPeriod.DAILY: (0, 0),
    RecurringTaskPeriod.WEEKLY: (1, 6),
    RecurringTaskPeriod.MONTHLY: (1, 31),
    RecurringTaskPeriod.QUARTERLY: (1, 31),
    RecurringTaskPeriod.YEARLY: (1, 31)
}


@dataclass(frozen=True)
class RecurringTaskDueAtDay(Value):
    """The due day for a recurring task."""

    _the_day: int

    @staticmethod
    def from_raw(period: RecurringTaskPeriod, recurring_task_due_at_day_raw: Optional[int]) -> 'RecurringTaskDueAtDay':
        """Validate and clean the recurring task due at day info."""
        if not recurring_task_due_at_day_raw:
            raise ModelValidationError("Expected the due day info to be non-null")

        bounds = _RECURRING_TASK_DUE_AT_DAY_BOUNDS[period]

        if recurring_task_due_at_day_raw < bounds[0] or recurring_task_due_at_day_raw > bounds[1]:
            raise ModelValidationError(
                f"Expected the due day info for {period} period to be a value between {bounds[0]} and {bounds[1]}")

        return RecurringTaskDueAtDay(recurring_task_due_at_day_raw)

    def as_int(self) -> int:
        """Return an int version of this."""
        return self._the_day

    def __str__(self) -> str:
        """String version of this."""
        return str(self._the_day)

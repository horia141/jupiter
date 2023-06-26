"""The due month for a recurring task."""
from dataclasses import dataclass
from typing import Dict, Final, Optional, Tuple

from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import Value

_RECURRING_TASK_DUE_AT_MONTH_BOUNDS: Final[
    Dict[RecurringTaskPeriod, Tuple[int, int]]
] = {
    RecurringTaskPeriod.DAILY: (0, 0),
    RecurringTaskPeriod.WEEKLY: (1, 6),
    RecurringTaskPeriod.MONTHLY: (1, 31),
    RecurringTaskPeriod.QUARTERLY: (1, 31),
    RecurringTaskPeriod.YEARLY: (1, 31),
}


@dataclass
class RecurringTaskDueAtMonth(Value):
    """The due month for a recurring task."""

    the_month: int

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_month = self._clean_the_month(
            RecurringTaskPeriod.YEARLY,
            self.the_month,
        )

    @staticmethod
    def from_raw(
        period: RecurringTaskPeriod,
        recurring_task_due_at_month_raw: Optional[int],
    ) -> "RecurringTaskDueAtMonth":
        """Validate and clean the recurring task due at month info."""
        if not recurring_task_due_at_month_raw:
            raise InputValidationError("Expected the due month info to be non-null")

        return RecurringTaskDueAtMonth(
            RecurringTaskDueAtMonth._clean_the_month(
                period,
                recurring_task_due_at_month_raw,
            ),
        )

    def as_int(self) -> int:
        """Return an int version of this."""
        return self.the_month

    def __str__(self) -> str:
        """String version of this."""
        return str(self.the_month)

    @staticmethod
    def _clean_the_month(period: RecurringTaskPeriod, the_month: int) -> int:
        bounds = _RECURRING_TASK_DUE_AT_MONTH_BOUNDS[period]

        if the_month < bounds[0] or the_month > bounds[1]:
            raise InputValidationError(
                f"Expected the due month info for {period} period to be a value between {bounds[0]} and {bounds[1]}",
            )

        return the_month
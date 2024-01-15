"""The due day for a recurring task."""
from typing import Dict, Final, Optional, Tuple

from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value

_RECURRING_TASK_DUE_AT_DAY_BOUNDS: Final[Dict[RecurringTaskPeriod, Tuple[int, int]]] = {
    RecurringTaskPeriod.DAILY: (0, 0),
    RecurringTaskPeriod.WEEKLY: (1, 6),
    RecurringTaskPeriod.MONTHLY: (1, 31),
    RecurringTaskPeriod.QUARTERLY: (1, 31),
    RecurringTaskPeriod.YEARLY: (1, 31),
}


@value
class RecurringTaskDueAtDay(AtomicValue):
    """The due day for a recurring task."""

    the_day: int

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_day = self._clean_the_day(RecurringTaskPeriod.YEARLY, self.the_day)

    @staticmethod
    def from_raw_with_period(
        period: RecurringTaskPeriod,
        recurring_task_due_at_day_raw: Optional[int],
    ) -> "RecurringTaskDueAtDay":
        """Validate and clean the recurring task due at day info."""
        if recurring_task_due_at_day_raw is None:
            raise InputValidationError("Expected the due day info to be non-null")

        return RecurringTaskDueAtDay(
            RecurringTaskDueAtDay._clean_the_day(period, recurring_task_due_at_day_raw),
        )

    @classmethod
    def base_type_hack(cls) -> type[Primitive]:
        return int

    @classmethod
    def from_raw(
        cls,
        value: Primitive,
    ) -> "RecurringTaskDueAtDay":
        """Validate and clean the recurring task due at day info."""
        if not isinstance(value, int):
            raise InputValidationError("Expected the due day info to int")

        return RecurringTaskDueAtDay(
            RecurringTaskDueAtDay._clean_the_day(RecurringTaskPeriod.YEARLY, value),
        )

    def to_primitive(self) -> Primitive:
        return self.the_day

    def as_int(self) -> int:
        """Return an int version of this."""
        return self.the_day

    def __str__(self) -> str:
        """String version of this."""
        return str(self.the_day)

    @staticmethod
    def _clean_the_day(period: RecurringTaskPeriod, the_day: int) -> int:
        bounds = _RECURRING_TASK_DUE_AT_DAY_BOUNDS[period]

        if the_day < bounds[0] or the_day > bounds[1]:
            raise InputValidationError(
                f"Expected the due day info for {period} period to be a value between {bounds[0]} and {bounds[1]} but was {the_day}",
            )

        return the_day

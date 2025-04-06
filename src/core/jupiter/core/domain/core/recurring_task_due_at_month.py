"""The due month for a recurring task."""

from typing import Final

from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)

_RECURRING_TASK_DUE_AT_MONTH_BOUNDS: Final[
    dict[RecurringTaskPeriod, tuple[int, int]]
] = {
    RecurringTaskPeriod.DAILY: (0, 0),
    RecurringTaskPeriod.WEEKLY: (1, 6),
    RecurringTaskPeriod.MONTHLY: (1, 31),
    RecurringTaskPeriod.QUARTERLY: (1, 31),
    RecurringTaskPeriod.YEARLY: (1, 31),
}


@value
class RecurringTaskDueAtMonth(AtomicValue[int]):
    """The due month for a recurring task."""

    value: int

    @staticmethod
    def first_of(period: RecurringTaskPeriod) -> "RecurringTaskDueAtMonth":
        """Return the first of the month for a period."""
        return RecurringTaskDueAtMonth(_RECURRING_TASK_DUE_AT_MONTH_BOUNDS[period][0])

    @staticmethod
    def end_of(period: RecurringTaskPeriod) -> "RecurringTaskDueAtMonth":
        """Return the end of the month for a period."""
        return RecurringTaskDueAtMonth(_RECURRING_TASK_DUE_AT_MONTH_BOUNDS[period][1])

    @staticmethod
    def build(period: RecurringTaskPeriod, value: int) -> "RecurringTaskDueAtMonth":
        """Constructor."""
        bounds = _RECURRING_TASK_DUE_AT_MONTH_BOUNDS[period]

        if value < bounds[0] or value > bounds[1]:
            raise InputValidationError(
                f"Expected the due month info for {period!s} period to be a value between {bounds[0]} and {bounds[1]}",
            )

        return RecurringTaskDueAtMonth(value)

    def as_int(self) -> int:
        """Return an int version of this."""
        return self.value

    def __str__(self) -> str:
        """String version of this."""
        return str(self.value)


class RecurringTaskDueAtMonthDatabaseEncoder(
    PrimitiveAtomicValueDatabaseEncoder[RecurringTaskDueAtMonth]
):
    """Encode to a database primitive."""

    def to_primitive(self, value: RecurringTaskDueAtMonth) -> Primitive:
        """Encode to a database primitive."""
        return value.value


class RecurringTaskDueAtMonthDatabaseDecoder(
    PrimitiveAtomicValueDatabaseDecoder[RecurringTaskDueAtMonth]
):
    """Decode from a database primitive."""

    def from_raw_int(self, value: int) -> RecurringTaskDueAtMonth:
        """Decode from a raw int."""
        return RecurringTaskDueAtMonth.build(RecurringTaskPeriod.YEARLY, value)

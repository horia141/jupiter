"""The due day for a recurring task."""
from typing import Final

from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)

_RECURRING_TASK_DUE_AT_DAY_BOUNDS: Final[dict[RecurringTaskPeriod, tuple[int, int]]] = {
    RecurringTaskPeriod.DAILY: (0, 0),
    RecurringTaskPeriod.WEEKLY: (1, 6),
    RecurringTaskPeriod.MONTHLY: (1, 31),
    RecurringTaskPeriod.QUARTERLY: (1, 31),
    RecurringTaskPeriod.YEARLY: (1, 31),
}


@value
class RecurringTaskDueAtDay(AtomicValue[int]):
    """The due day for a recurring task."""

    value: int

    @staticmethod
    def first_of(period: RecurringTaskPeriod) -> "RecurringTaskDueAtDay":
        """Return the first day of the period."""
        return RecurringTaskDueAtDay.build(
            period, _RECURRING_TASK_DUE_AT_DAY_BOUNDS[period][0]
        )

    @staticmethod
    def end_of(period: RecurringTaskPeriod) -> "RecurringTaskDueAtDay":
        """Return the last day of the period."""
        return RecurringTaskDueAtDay.build(
            period, _RECURRING_TASK_DUE_AT_DAY_BOUNDS[period][1]
        )

    @staticmethod
    def build(period: RecurringTaskPeriod, value: int) -> "RecurringTaskDueAtDay":
        """Constructor."""
        bounds = _RECURRING_TASK_DUE_AT_DAY_BOUNDS[period]

        if value < bounds[0] or value > bounds[1]:
            raise InputValidationError(
                f"Expected the due day info for {period!s} period to be a value between {bounds[0]} and {bounds[1]} but was {value}",
            )

        return RecurringTaskDueAtDay(value)

    def as_int(self) -> int:
        """Return an int version of this."""
        return self.value

    def __str__(self) -> str:
        """String version of this."""
        return str(self.value)


class RecurringTaskDueAtDayDatabaseEncoder(
    PrimitiveAtomicValueDatabaseEncoder[RecurringTaskDueAtDay]
):
    """Encode to a database primitive."""

    def to_primitive(self, value: RecurringTaskDueAtDay) -> Primitive:
        """Encode to a database primitive."""
        return value.value


class RecurringTaskDueAtDayDatabaseDecoder(
    PrimitiveAtomicValueDatabaseDecoder[RecurringTaskDueAtDay]
):
    """Decode from a database primitive."""

    def from_raw_int(self, value: int) -> RecurringTaskDueAtDay:
        """Decode from a raw int."""
        return RecurringTaskDueAtDay.build(RecurringTaskPeriod.YEARLY, value)

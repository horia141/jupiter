"""The due month for a recurring task."""
from typing import Dict, Final, Optional, Tuple

from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import PrimitiveAtomicValueDatabaseDecoder, PrimitiveAtomicValueDatabaseEncoder

_RECURRING_TASK_DUE_AT_MONTH_BOUNDS: Final[
    Dict[RecurringTaskPeriod, Tuple[int, int]]
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
        return RecurringTaskDueAtMonth(period, _RECURRING_TASK_DUE_AT_MONTH_BOUNDS[period][0])
    
    @staticmethod
    def end_of(period: RecurringTaskPeriod) -> "RecurringTaskDueAtMonth":
        return RecurringTaskDueAtMonth(period, _RECURRING_TASK_DUE_AT_MONTH_BOUNDS[period][1])

    def __init__(self, period: RecurringTaskPeriod, value: int) -> None:
        bounds = _RECURRING_TASK_DUE_AT_MONTH_BOUNDS[period]

        if value < bounds[0] or value > bounds[1]:
            raise InputValidationError(
                f"Expected the due month info for {str(period)} period to be a value between {bounds[0]} and {bounds[1]}",
            )
        
        self.value = value

    def as_int(self) -> int:
        """Return an int version of this."""
        return self.value

    def __str__(self) -> str:
        """String version of this."""
        return str(self.value)




class RecurringTaskDueAtMonthDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[RecurringTaskDueAtMonth]):

    def to_primitive(self, value: RecurringTaskDueAtMonth) -> Primitive:
        return value.value
    

class RecurringTaskDueAtMonthDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[RecurringTaskDueAtMonth]):

    def from_raw_int(self, value: int) -> RecurringTaskDueAtMonth:
        return RecurringTaskDueAtMonth(RecurringTaskPeriod.YEARLY, value)

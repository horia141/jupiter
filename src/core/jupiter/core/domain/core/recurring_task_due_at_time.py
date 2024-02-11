"""The due time for a recurring task."""
import re
from typing import Final, Pattern

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import PrimitiveAtomicValueDatabaseDecoder, PrimitiveAtomicValueDatabaseEncoder

_DUE_AT_TIME_RE: Final[Pattern[str]] = re.compile(r"^[0-9][0-9]:[0-9][0-9]$")


@value
class RecurringTaskDueAtTime(AtomicValue[str]):
    """The due time for a recurring task."""

    the_time: str

    def __str__(self) -> str:
        """String version of this."""
        return self.the_time




class RecurringTaskDueAtTimeDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[RecurringTaskDueAtTime]):

    def to_primitive(self, value: RecurringTaskDueAtTime) -> Primitive:
        return value.the_time
    

class RecurringTaskDueAtTimeDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[RecurringTaskDueAtTime]):

    def from_raw_str(self, value: str) -> RecurringTaskDueAtTime:
        the_time = value.strip().lower()

        if len(the_time) == 0:
            raise InputValidationError("Expected due time info to be non-empty")

        if not _DUE_AT_TIME_RE.match(the_time):
            raise InputValidationError(
                f"Expected due time info '{the_time}' to "
                + f"match '{_DUE_AT_TIME_RE.pattern}'",
            )

        return RecurringTaskDueAtTime(the_time)

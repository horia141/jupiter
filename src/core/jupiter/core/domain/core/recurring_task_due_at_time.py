"""The due time for a recurring task."""
import re
from typing import Final, Pattern

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value

_DUE_AT_TIME_RE: Final[Pattern[str]] = re.compile(r"^[0-9][0-9]:[0-9][0-9]$")


@value
class RecurringTaskDueAtTime(AtomicValue):
    """The due time for a recurring task."""

    the_time: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_time = self._clean_the_time(self.the_time)

    @classmethod
    def from_raw(
        cls,
        value: Primitive,
    ) -> "RecurringTaskDueAtTime":
        """Validate and clean the due at time info."""
        if not isinstance(value, str):
            raise InputValidationError("Expected the due time info to be string")

        return RecurringTaskDueAtTime(
            RecurringTaskDueAtTime._clean_the_time(value),
        )

    def to_primitive(self) -> Primitive:
        return self.the_time

    def __str__(self) -> str:
        """String version of this."""
        return self.the_time

    @staticmethod
    def _clean_the_time(the_time: str) -> str:
        the_time = the_time.strip().lower()

        if len(the_time) == 0:
            raise InputValidationError("Expected due time info to be non-empty")

        if not _DUE_AT_TIME_RE.match(the_time):
            raise InputValidationError(
                f"Expected due time info '{the_time}' to "
                + f"match '{_DUE_AT_TIME_RE.pattern}'",
            )

        return the_time

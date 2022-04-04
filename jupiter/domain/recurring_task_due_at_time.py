"""The due time for a recurring task."""
import re
from dataclasses import dataclass
from typing import Final, Optional, Pattern

from jupiter.framework.errors import InputValidationError
from jupiter.framework.value import Value

_DUE_AT_TIME_RE: Final[Pattern[str]] = re.compile(r"^[0-9][0-9]:[0-9][0-9]$")


@dataclass(frozen=True)
class RecurringTaskDueAtTime(Value):
    """The due time for a recurring task."""

    _the_time: str

    @staticmethod
    def from_raw(
        recurring_task_due_at_time_raw: Optional[str],
    ) -> "RecurringTaskDueAtTime":
        """Validate and clean the due at time info."""
        if not recurring_task_due_at_time_raw:
            raise InputValidationError("Expected the due time info to be non-null")

        recurring_task_due_at_time_str: str = (
            recurring_task_due_at_time_raw.strip().lower()
        )

        if len(recurring_task_due_at_time_str) == 0:
            raise InputValidationError("Expected due time info to be non-empty")

        if not _DUE_AT_TIME_RE.match(recurring_task_due_at_time_str):
            raise InputValidationError(
                f"Expected due time info '{recurring_task_due_at_time_raw}' to "
                + f"match '{_DUE_AT_TIME_RE.pattern}'"
            )

        return RecurringTaskDueAtTime(recurring_task_due_at_time_str)

    def __str__(self) -> str:
        """String version of this."""
        return self._the_time

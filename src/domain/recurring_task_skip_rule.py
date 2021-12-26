"""The rules for skipping a recurring task."""
from dataclasses import dataclass
from typing import Optional

from framework.errors import InputValidationError
from framework.value import Value


@dataclass(frozen=True)
class RecurringTaskSkipRule(Value):
    """The rules for skipping a recurring task."""

    _skip_rule: str

    @staticmethod
    def from_raw(recurring_task_skip_rule_raw: Optional[str]) -> 'RecurringTaskSkipRule':
        """Validate and clean the recurring task skip rule."""
        if not recurring_task_skip_rule_raw:
            raise InputValidationError("Expected the skip rule info to be non-null")

        return RecurringTaskSkipRule(recurring_task_skip_rule_raw.strip().lower())

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._skip_rule

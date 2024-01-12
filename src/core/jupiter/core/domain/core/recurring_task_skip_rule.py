"""The rules for skipping a recurring task."""
from typing import Optional

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value


@value
class RecurringTaskSkipRule(AtomicValue):
    """The rules for skipping a recurring task."""

    skip_rule: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.skip_rule = self._clean_skip_rule(self.skip_rule)

    @staticmethod
    def from_raw(
        recurring_task_skip_rule_raw: Optional[str],
    ) -> "RecurringTaskSkipRule":
        """Validate and clean the recurring task skip rule."""
        if not recurring_task_skip_rule_raw:
            raise InputValidationError("Expected the skip rule info to be non-null")

        return RecurringTaskSkipRule(
            RecurringTaskSkipRule._clean_skip_rule(recurring_task_skip_rule_raw),
        )

    def to_primitive(self) -> Primitive:
        return self.skip_rule

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.skip_rule

    @staticmethod
    def _clean_skip_rule(recurring_task_skip_rule_raw: str) -> str:
        return recurring_task_skip_rule_raw.strip().lower()

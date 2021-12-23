"""The type of recurring class."""
import enum
from functools import lru_cache
from typing import Optional, Iterable

from framework.errors import ModelValidationError
from framework.value import Value


@enum.unique
class RecurringTaskType(Value, enum.Enum):
    """The type of recurring class."""
    CHORE = "chore"
    HABIT = "habit"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return str(self.value).capitalize()

    @staticmethod
    def from_raw(recurring_task_type_raw: Optional[str]) -> 'RecurringTaskType':
        """Validate and clean the recurring task type."""
        if not recurring_task_type_raw:
            raise ModelValidationError("Expected big plan status to be non-null")

        recurring_task_type_str: str = recurring_task_type_raw.strip().lower()

        if recurring_task_type_str not in RecurringTaskType.all_values():
            raise ModelValidationError(
                f"Expected recurring task type '{recurring_task_type_raw}' to be " +
                f"one of '{','.join(RecurringTaskType.all_values())}'")

        return RecurringTaskType(recurring_task_type_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for difficulties."""
        return frozenset(st.value for st in RecurringTaskType)

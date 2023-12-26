"""A period for a particular task."""
from functools import lru_cache, total_ordering
from typing import Iterable, List, Optional, cast

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
@total_ordering
class RecurringTaskPeriod(EnumValue):
    """A period for a particular task."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

    def to_nice(self) -> str:
        """A prettier version of the value."""
        return str(self.value).capitalize()

    @staticmethod
    def from_raw(recurring_task_period_raw: Optional[str]) -> "RecurringTaskPeriod":
        """Validate and clean the recurring task period."""
        if not recurring_task_period_raw:
            raise InputValidationError("Expected recurring task period to be non-null")

        recurring_task_period_str: str = recurring_task_period_raw.strip().lower()

        if recurring_task_period_str not in RecurringTaskPeriod.all_values():
            raise InputValidationError(
                f"Expected recurring task period '{recurring_task_period_raw}' to be "
                + f"one of '{','.join(RecurringTaskPeriod.all_values())}'",
            )

        return RecurringTaskPeriod(recurring_task_period_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for difficulties."""
        return list(p.value for p in RecurringTaskPeriod)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, RecurringTaskPeriod):
            raise Exception(
                f"Cannot compare an entity id with {other.__class__.__name__}",
            )

        all_values = cast(List[str], self.all_values())

        return all_values.index(self.value) < all_values.index(other.value)

    def __str__(self) -> str:
        """String form."""
        return str(self.value)

"""A period for a particular task."""
from functools import total_ordering

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

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, RecurringTaskPeriod):
            raise Exception(
                f"Cannot compare an entity id with {other.__class__.__name__}",
            )

        all_values = self.get_all_values()

        return all_values.index(self.value) < all_values.index(other.value)

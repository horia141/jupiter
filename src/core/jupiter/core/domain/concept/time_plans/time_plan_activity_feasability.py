"""The feasability of a particular activity within a plan."""

from functools import total_ordering

from jupiter.core.framework.value import EnumValue, enum_value


@total_ordering
@enum_value
class TimePlanActivityFeasability(EnumValue):
    """The feasability of a particular activity within a plan."""

    MUST_DO = "must-do"
    NICE_TO_HAVE = "nice-to-have"
    STRETCH = "stretch"

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, TimePlanActivityFeasability):
            raise Exception(
                f"Cannot compare with {other.__class__.__name__}",
            )

        all_values = self.get_all_values()

        return all_values.index(self.value) < all_values.index(other.value)

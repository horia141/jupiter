"""The kind of an activity."""

from functools import total_ordering

from jupiter.core.framework.value import EnumValue, enum_value


@total_ordering
@enum_value
class TimePlanActivityKind(EnumValue):
    """The kind of a time plan activity."""

    FINISH = "finish"
    MAKE_PROGRESS = "make-progress"

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, TimePlanActivityKind):
            raise Exception(
                f"Cannot compare with {other.__class__.__name__}",
            )

        all_values = self.get_all_values()

        return all_values.index(self.value) < all_values.index(other.value)

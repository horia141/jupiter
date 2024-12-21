"""The difficulty of a particular task."""
from functools import total_ordering

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
@total_ordering
class Difficulty(EnumValue):
    """The difficulty of a particular task."""

    HARD = "hard"
    MEDIUM = "medium"
    EASY = "easy"

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, Difficulty):
            raise Exception(
                f"Cannot compare a difficulty with {other.__class__.__name__}",
            )

        all_values = self.get_all_values()

        return all_values.index(self.value) < all_values.index(other.value)

"""The difficulty of a particular task."""
import enum
from functools import lru_cache, total_ordering
from typing import Optional, Iterable, cast, List

from jupiter.framework.errors import InputValidationError


@enum.unique
@total_ordering
class Difficulty(enum.Enum):
    """The difficulty of a particular task."""

    HARD = "hard"
    MEDIUM = "medium"
    EASY = "easy"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return str(self.value).capitalize()

    @staticmethod
    def from_raw(difficulty_raw: Optional[str]) -> "Difficulty":
        """Validate and clean the difficulty."""
        if not difficulty_raw:
            raise InputValidationError("Expected difficulty to be non-null")

        difficulty_str: str = difficulty_raw.strip().lower()

        if difficulty_str not in Difficulty.all_values():
            raise InputValidationError(
                f"Expected difficulty '{difficulty_raw}' to be one of '{','.join(Difficulty.all_values())}'"
            )

        return Difficulty(difficulty_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for difficulties."""
        return list(st.value for st in Difficulty)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, Difficulty):
            raise Exception(
                f"Cannot compare a difficulty with {other.__class__.__name__}"
            )

        all_values = cast(List[str], self.all_values())

        return all_values.index(self.value) < all_values.index(other.value)

    def __str__(self) -> str:
        """String form."""
        return str(self.value)

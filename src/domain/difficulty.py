"""The difficulty of a particular task."""
import enum
from functools import lru_cache
from typing import Optional, Iterable

from framework.errors import ModelValidationError


@enum.unique
class Difficulty(enum.Enum):
    """The difficulty of a particular task."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return str(self.value).capitalize()

    @staticmethod
    def from_raw(difficulty_raw: Optional[str]) -> 'Difficulty':
        """Validate and clean the difficulty."""
        if not difficulty_raw:
            raise ModelValidationError("Expected difficulty to be non-null")

        difficulty_str: str = difficulty_raw.strip().lower()

        if difficulty_str not in Difficulty.all_values():
            raise ModelValidationError(
                f"Expected difficulty '{difficulty_raw}' to be one of '{','.join(Difficulty.all_values())}'")

        return Difficulty(difficulty_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for difficulties."""
        return frozenset(st.value for st in Difficulty)

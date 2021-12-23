"""The Eisenhower status of a particular task."""
import enum
from functools import lru_cache
from typing import Optional, Iterable

from framework.errors import ModelValidationError


@enum.unique
class Eisen(enum.Enum):
    """The Eisenhower status of a particular task."""
    IMPORTANT = "important"
    URGENT = "urgent"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return str(self.value).capitalize()

    @staticmethod
    def from_raw(eisen_raw: Optional[str]) -> 'Eisen':
        """Validate and clean a raw person relationship value."""
        if not eisen_raw:
            raise ModelValidationError("Expected Eisenhower status to be non-null")

        eisen_str: str = eisen_raw.strip().lower()

        if eisen_str not in Eisen.all_values():
            raise ModelValidationError(
                f"Expected Eisenhower status '{eisen_raw}' to be one of '{','.join(Eisen.all_values())}'")

        return Eisen(eisen_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for eisen."""
        return frozenset(st.value for st in Eisen)

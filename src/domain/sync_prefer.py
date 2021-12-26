"""The source of data to prefer for a sync operation."""
import enum
from functools import lru_cache
from typing import Iterable, Optional

from framework.errors import InputValidationError


@enum.unique
class SyncPrefer(enum.Enum):
    """The source of data to prefer for a sync operation."""
    LOCAL = "local"
    NOTION = "notion"

    @staticmethod
    def from_raw(sync_prefer_raw: Optional[str]) -> 'SyncPrefer':
        """Validate and clean the big plan status."""
        if not sync_prefer_raw:
            raise InputValidationError("Expected sync prefer to be non-null")

        sync_prefer_str: str = sync_prefer_raw.strip().lower()

        if sync_prefer_str not in SyncPrefer.all_values():
            raise InputValidationError(
                f"Expected sync prefer '{sync_prefer_raw}' to be one of '{','.join(SyncPrefer.all_values())}'")

        return SyncPrefer(sync_prefer_str)

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for difficulties."""
        return frozenset(st.value for st in SyncPrefer)

"""A generic notion id."""
import uuid
from dataclasses import dataclass
from functools import total_ordering
from typing import Optional

from framework.errors import InputValidationError
from framework.value import Value


@dataclass(frozen=True)
@total_ordering
class NotionId(Value):
    """A generic Notion id."""

    _the_id: str

    @staticmethod
    def make_brand_new() -> 'NotionId':
        """Make a new NotionId."""
        return NotionId(str(uuid.uuid4()))

    @staticmethod
    def from_raw(notion_id_raw: Optional[str]) -> 'NotionId':
        """Validate and clean an notion id."""
        if not notion_id_raw:
            raise InputValidationError("Expected Notion id to be non-null")

        notion_id: str = notion_id_raw.strip()

        if len(notion_id) == 0:
            raise InputValidationError("Expected notion id to be non-empty")

        return NotionId(notion_id)

    def as_int(self) -> int:
        """Return an integer form of this, if possible."""
        return int(self._the_id)

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, NotionId):
            raise Exception(f"Cannot compare an notion id with {other.__class__.__name__}")
        return self._the_id < other._the_id

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._the_id


BAD_NOTION_ID = NotionId("bad-notion-id")

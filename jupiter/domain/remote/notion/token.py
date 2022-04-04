"""The token for accessing Notion."""
import re
from dataclasses import dataclass
from typing import Final, Pattern, Optional

from jupiter.framework.errors import InputValidationError
from jupiter.framework.value import Value

_NOTION_TOKEN_RE: Final[Pattern[str]] = re.compile(r"^[0-9a-f]+$")


@dataclass(frozen=True)
class NotionToken(Value):
    """The token for accessing Notion."""

    _the_token: str

    @staticmethod
    def from_raw(notion_token_raw: Optional[str]) -> "NotionToken":
        """Validate and clean a workspace token."""
        if not notion_token_raw:
            raise InputValidationError("Expected Notion token to be non-null")

        notion_token: str = notion_token_raw.strip().lower()

        if len(notion_token) == 0:
            raise InputValidationError("Expected workspace token to be non-empty")

        if not _NOTION_TOKEN_RE.match(notion_token):
            raise InputValidationError(
                f"Expected workspace token '{notion_token}' to match '{_NOTION_TOKEN_RE.pattern}"
            )

        return NotionToken(notion_token)

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._the_token

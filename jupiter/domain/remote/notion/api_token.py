"""The token for accessing Notion via its API."""
import re
from dataclasses import dataclass
from typing import Final, Pattern, Optional

from jupiter.framework.errors import InputValidationError
from jupiter.framework.value import Value

_NOTION_API_TOKEN_RE: Final[Pattern[str]] = re.compile(r"^secret_[0-9a-zA-Z]+$")


@dataclass(frozen=True)
class NotionApiToken(Value):
    """The token for accessing Notion via its API."""

    _the_api_token: str

    @staticmethod
    def from_raw(notion_api_token_raw: Optional[str]) -> "NotionApiToken":
        """Validate and clean a Notion API token."""
        if not notion_api_token_raw:
            raise InputValidationError("Expected Notion API token to be non-null")

        notion_api_token: str = notion_api_token_raw.strip()

        if len(notion_api_token) == 0:
            raise InputValidationError("Expected Notion API to be non-empty")

        if not _NOTION_API_TOKEN_RE.match(notion_api_token):
            raise InputValidationError(
                f"Expected workspace token '{notion_api_token}' to match '{_NOTION_API_TOKEN_RE.pattern}"
            )

        return NotionApiToken(notion_api_token)

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._the_api_token

"""A Slack user name."""
import re
from dataclasses import dataclass
from typing import Final, Pattern, Optional

from jupiter.framework.errors import InputValidationError
from jupiter.framework.value import Value

_SLACK_USER_NAME_RE: Final[Pattern[str]] = re.compile(r"^.+$")


@dataclass(frozen=True)
class SlackUserName(Value):
    """A Slack user name."""

    _the_name: str

    @staticmethod
    def from_raw(slack_user_name_raw: Optional[str]) -> "SlackUserName":
        """Validate and clean a Slack user name."""
        if not slack_user_name_raw:
            raise InputValidationError("Expected Slack user name to be non-null")

        slack_user_name: str = " ".join(
            word for word in slack_user_name_raw.strip().split(" ") if len(word) > 0
        )

        if len(slack_user_name) == 0:
            raise InputValidationError("Expected Slack user name to be non-empty")

        if not _SLACK_USER_NAME_RE.match(slack_user_name):
            raise InputValidationError(
                f"Expected Slack user name '{slack_user_name_raw}' to match '{_SLACK_USER_NAME_RE.pattern}"
            )

        return SlackUserName(slack_user_name)

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._the_name

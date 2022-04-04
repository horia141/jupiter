"""A Slack channel name."""
import re
from dataclasses import dataclass
from typing import Final, Pattern, Optional

from jupiter.framework.errors import InputValidationError
from jupiter.framework.value import Value

_SLACK_CHANNEL_NAME_RE: Final[Pattern[str]] = re.compile(r"^[a-z0-9._-]+$")


@dataclass(frozen=True)
class SlackChannelName(Value):
    """A Slack channel name."""

    _the_name: str

    @staticmethod
    def from_raw(slack_channel_name_raw: Optional[str]) -> "SlackChannelName":
        """Validate and clean a Slack channel name."""
        if not slack_channel_name_raw:
            raise InputValidationError("Expected Slack channel name to be non-null")

        slack_channel_name: str = " ".join(
            word for word in slack_channel_name_raw.strip().split(" ") if len(word) > 0
        )

        if len(slack_channel_name) == 0:
            raise InputValidationError("Expected Slack channel name to be non-empty")

        if not _SLACK_CHANNEL_NAME_RE.match(slack_channel_name):
            raise InputValidationError(
                f"Expected Slack channel name '{slack_channel_name_raw}' to match '{_SLACK_CHANNEL_NAME_RE.pattern}"
            )

        return SlackChannelName(slack_channel_name)

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._the_name

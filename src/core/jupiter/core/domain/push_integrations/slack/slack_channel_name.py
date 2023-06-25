"""A Slack channel name."""
import re
from dataclasses import dataclass
from typing import Final, Optional, Pattern

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import Value

_SLACK_CHANNEL_NAME_RE: Final[Pattern[str]] = re.compile(r"^[a-z0-9._-]+$")


@dataclass(eq=True, unsafe_hash=True)
class SlackChannelName(Value):
    """A Slack channel name."""

    the_name: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_name = self._clean_the_name(self.the_name)

    @staticmethod
    def from_raw(slack_channel_name_raw: Optional[str]) -> "SlackChannelName":
        """Validate and clean a Slack channel name."""
        if not slack_channel_name_raw:
            raise InputValidationError("Expected Slack channel name to be non-null")

        return SlackChannelName(
            SlackChannelName._clean_the_name(slack_channel_name_raw),
        )

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.the_name

    @staticmethod
    def _clean_the_name(slack_channel_name_raw: str) -> str:
        slack_channel_name: str = " ".join(
            word for word in slack_channel_name_raw.strip().split(" ") if len(word) > 0
        )

        if len(slack_channel_name) == 0:
            raise InputValidationError("Expected Slack channel name to be non-empty")

        if not _SLACK_CHANNEL_NAME_RE.match(slack_channel_name):
            raise InputValidationError(
                f"Expected Slack channel name '{slack_channel_name_raw}' to match '{_SLACK_CHANNEL_NAME_RE.pattern}",
            )

        return slack_channel_name

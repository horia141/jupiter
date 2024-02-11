"""A Slack channel name."""
import re
from typing import Final, Pattern

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, hashable_value

_SLACK_CHANNEL_NAME_RE: Final[Pattern[str]] = re.compile(r"^[a-z0-9._-]+$")


@hashable_value
class SlackChannelName(AtomicValue):
    """A Slack channel name."""

    the_name: str

    @classmethod
    def base_type_hack(cls) -> type[Primitive]:
        return str

    @classmethod
    def from_raw(cls, value: Primitive) -> "SlackChannelName":
        """Validate and clean a Slack channel name."""
        if not isinstance(value, str):
            raise InputValidationError("Expected Slack channel name to be a string")

        return SlackChannelName(
            SlackChannelName._clean_the_name(value),
        )

    def to_primitive(self) -> Primitive:
        return self.the_name

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

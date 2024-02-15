"""A Slack channel name."""
import re
from typing import Final, Pattern

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, hashable_value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)

_SLACK_CHANNEL_NAME_RE: Final[Pattern[str]] = re.compile(r"^[a-z0-9._-]+$")


@hashable_value
class SlackChannelName(AtomicValue[str]):
    """A Slack channel name."""

    the_name: str

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.the_name


class SlackChannelNameDatabaseEncoder(
    PrimitiveAtomicValueDatabaseEncoder[SlackChannelName]
):
    def to_primitive(self, value: SlackChannelName) -> Primitive:
        return value.the_name


class SlackChannelNameDatabaseDecoder(
    PrimitiveAtomicValueDatabaseDecoder[SlackChannelName]
):
    def from_raw_str(self, value: str) -> SlackChannelName:
        slack_channel_name: str = " ".join(
            word for word in value.strip().split(" ") if len(word) > 0
        )

        if len(slack_channel_name) == 0:
            raise InputValidationError("Expected Slack channel name to be non-empty")

        if not _SLACK_CHANNEL_NAME_RE.match(slack_channel_name):
            raise InputValidationError(
                f"Expected Slack channel name '{value}' to match '{_SLACK_CHANNEL_NAME_RE.pattern}",
            )

        return SlackChannelName(slack_channel_name)

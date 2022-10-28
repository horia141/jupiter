"""A Slack user name."""
from dataclasses import dataclass

from jupiter.domain.entity_name import EntityName


@dataclass(frozen=True)
class SlackUserName(EntityName):
    """A Slack user name."""

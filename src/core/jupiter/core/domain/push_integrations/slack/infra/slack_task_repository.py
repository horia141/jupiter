"""A repository of Slack tasks."""
import abc

from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class SlackTaskRepository(LeafEntityRepository[SlackTask], abc.ABC):
    """A repository of slack tasks."""

"""A repository of Slack tasks."""
import abc

from jupiter.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.framework.repository import LeafEntityRepository, LeafEntityNotFoundError


class SlackTaskNotFoundError(LeafEntityNotFoundError):
    """Error raised when a slack task is not found."""


class SlackTaskRepository(LeafEntityRepository[SlackTask], abc.ABC):
    """A repository of slack tasks."""

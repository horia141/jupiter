"""A Notion manager for slack tasks."""
from jupiter.domain.push_integrations.group.notion_push_integration_group import (
    NotionPushIntegrationGroup,
)
from jupiter.domain.push_integrations.slack.notion_slack_task import NotionSlackTask
from jupiter.domain.push_integrations.slack.notion_slack_task_collection import (
    NotionSlackTaskCollection,
)
from jupiter.framework.notion_manager import (
    NotionLeafEntityNotFoundError,
    ParentTrunkLeafNotionManager,
)


class NotionSlackTaskNotFoundError(NotionLeafEntityNotFoundError):
    """Exception raised when a Notion slack task was not found."""


class SlackTaskNotionManager(
    ParentTrunkLeafNotionManager[
        NotionPushIntegrationGroup, NotionSlackTaskCollection, NotionSlackTask, None
    ]
):
    """A manager of Notion-side slack tasks."""

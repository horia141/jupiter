"""A Notion manager for email tasks."""
from jupiter.domain.push_integrations.group.notion_push_integration_group import (
    NotionPushIntegrationGroup,
)
from jupiter.domain.push_integrations.email.notion_email_task import NotionEmailTask
from jupiter.domain.push_integrations.email.notion_email_task_collection import (
    NotionEmailTaskCollection,
)
from jupiter.framework.notion_manager import (
    NotionLeafEntityNotFoundError,
    ParentTrunkLeafNotionManager,
)


class NotionEmailTaskNotFoundError(NotionLeafEntityNotFoundError):
    """Exception raised when a Notion email task was not found."""


class EmailTaskNotionManager(
    ParentTrunkLeafNotionManager[
        NotionPushIntegrationGroup,
        NotionEmailTaskCollection,
        NotionEmailTask,
    ]
):
    """A manager of Notion-side email tasks."""

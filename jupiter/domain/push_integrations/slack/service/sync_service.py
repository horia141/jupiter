"""A service for syncing between Notion and local for slack push integration entities."""
from jupiter.domain.notion_sync_service import TrunkLeafNotionSyncService
from jupiter.domain.push_integrations.group.notion_push_integration_group import (
    NotionPushIntegrationGroup,
)
from jupiter.domain.push_integrations.slack.infra.slack_task_notion_manager import (
    SlackTaskNotionManager,
)
from jupiter.domain.push_integrations.slack.notion_slack_task import NotionSlackTask
from jupiter.domain.push_integrations.slack.notion_slack_task_collection import (
    NotionSlackTaskCollection,
)
from jupiter.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.domain.storage_engine import DomainStorageEngine


class SlackTaskSyncService(
    TrunkLeafNotionSyncService[
        SlackTaskCollection,
        SlackTask,
        NotionPushIntegrationGroup,
        NotionSlackTaskCollection,
        NotionSlackTask,
        None,
        NotionSlackTask.InverseInfo,
    ]
):
    """The service class for dealing with slack tasks."""

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        slack_task_notion_manager: SlackTaskNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(
            SlackTaskCollection,
            SlackTask,
            "slack task",
            NotionSlackTask,
            storage_engine,
            slack_task_notion_manager,
        )

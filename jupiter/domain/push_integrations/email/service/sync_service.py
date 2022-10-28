"""A service for syncing between Notion and local for email push integration entities."""
from jupiter.domain.notion_sync_service import TrunkLeafNotionSyncService
from jupiter.domain.push_integrations.group.notion_push_integration_group import (
    NotionPushIntegrationGroup,
)
from jupiter.domain.push_integrations.email.infra.email_task_notion_manager import (
    EmailTaskNotionManager,
)
from jupiter.domain.push_integrations.email.notion_email_task import NotionEmailTask
from jupiter.domain.push_integrations.email.notion_email_task_collection import (
    NotionEmailTaskCollection,
)
from jupiter.domain.push_integrations.email.email_task import EmailTask
from jupiter.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.domain.storage_engine import DomainStorageEngine


class EmailTaskSyncService(
    TrunkLeafNotionSyncService[
        EmailTaskCollection,
        EmailTask,
        NotionPushIntegrationGroup,
        NotionEmailTaskCollection,
        NotionEmailTask,
        None,
        NotionEmailTask.InverseInfo,
    ]
):
    """The service class for dealing with email tasks."""

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        email_task_notion_manager: EmailTaskNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(
            EmailTaskCollection,
            EmailTask,
            "email task",
            NotionEmailTask,
            storage_engine,
            email_task_notion_manager,
        )

"""A Notion manager for push integrations groups."""
import abc

from jupiter.domain.push_integrations.group.notion_push_integration_group import (
    NotionPushIntegrationGroup,
)
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace


class PushIntegrationGroupNotionManager(abc.ABC):
    """A Notion manager for push integrations groups."""

    @abc.abstractmethod
    def upsert_push_integration_group(
        self,
        workspace: NotionWorkspace,
        push_integration_group: NotionPushIntegrationGroup,
    ) -> NotionPushIntegrationGroup:
        """Upsert the root Notion structure."""

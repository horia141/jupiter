"""The Notion manager for the push integration group."""
from typing import ClassVar, Final

from jupiter.domain.push_integrations.group.infra.push_integration_group_notion_manager import \
    PushIntegrationGroupNotionManager
from jupiter.domain.push_integrations.group.notion_push_integration_group import NotionPushIntegrationGroup
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.pages_manager import NotionPagesManager


class NotionPushIntegrationGroupsManager(PushIntegrationGroupNotionManager):
    """The Notion manager for the push integration group."""

    _KEY: ClassVar[str] = "push-integration-groups"
    _NAME: ClassVar[str] = "Push Integrations"
    _PAGE_ICON: ClassVar[str] = "⚙️"

    _pages_manager: Final[NotionPagesManager]

    def __init__(self, pages_manager: NotionPagesManager) -> None:
        """Constructor."""
        self._pages_manager = pages_manager

    def upsert_push_integration_group(
            self, workspace: NotionWorkspace,
            push_integration_group: NotionPushIntegrationGroup) -> NotionPushIntegrationGroup:
        """Upsert the root Notion structure."""
        push_integration_group_page = \
            self._pages_manager.upsert_page(
                key=NotionLockKey(f"{self._KEY}:{push_integration_group.ref_id}"),
                name=self._NAME,
                icon=self._PAGE_ICON,
                parent_page_notion_id=workspace.notion_id)

        return NotionPushIntegrationGroup(
            notion_id=push_integration_group_page.notion_id,
            ref_id=workspace.ref_id)

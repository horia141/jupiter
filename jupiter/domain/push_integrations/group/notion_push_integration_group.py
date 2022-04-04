"""The Notion-side representation of the push integrations group."""
from dataclasses import dataclass

from jupiter.domain.push_integrations.group.push_integration_group import PushIntegrationGroup
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.notion import NotionTrunkEntity


@dataclass(frozen=True)
class NotionPushIntegrationGroup(NotionTrunkEntity[PushIntegrationGroup]):
    """The Notion-side representation of the push integrations group."""

    @staticmethod
    def new_notion_entity(entity: PushIntegrationGroup) -> 'NotionPushIntegrationGroup':
        """Construct a new Notion row from a given entity."""
        return NotionPushIntegrationGroup(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id)

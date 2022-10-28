"""A Notion email task collection."""
from dataclasses import dataclass

from jupiter.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.notion import NotionTrunkEntity


@dataclass(frozen=True)
class NotionEmailTaskCollection(NotionTrunkEntity[EmailTaskCollection]):
    """A email task collection on Notion-side."""

    @staticmethod
    def new_notion_entity(entity: EmailTaskCollection) -> "NotionEmailTaskCollection":
        """Construct a new Notion row from a given entity."""
        return NotionEmailTaskCollection(notion_id=BAD_NOTION_ID, ref_id=entity.ref_id)

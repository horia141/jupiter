"""A inbox task collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.notion import NotionTrunkEntity


@dataclass(frozen=True)
class NotionInboxTaskCollection(NotionTrunkEntity[InboxTaskCollection]):
    """A inbox task collection on Notion-side."""

    @staticmethod
    def new_notion_entity(entity: InboxTaskCollection) -> 'NotionInboxTaskCollection':
        """Construct a new Notion row from a given entity."""
        return NotionInboxTaskCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id)

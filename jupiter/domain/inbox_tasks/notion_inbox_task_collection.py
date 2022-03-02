"""A inbox task collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.notion import NotionEntity
from jupiter.framework.base.notion_id import BAD_NOTION_ID


@dataclass(frozen=True)
class NotionInboxTaskCollection(NotionEntity[InboxTaskCollection]):
    """A inbox task collection on Notion-side."""

    @staticmethod
    def new_notion_row(entity: InboxTaskCollection) -> 'NotionInboxTaskCollection':
        """Construct a new Notion row from a given entity."""
        return NotionInboxTaskCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id)

    def apply_to_entity(
            self, entity: InboxTaskCollection, modification_time: Timestamp) -> InboxTaskCollection:
        """Obtain the entity form of this, with a possible error."""
        return entity

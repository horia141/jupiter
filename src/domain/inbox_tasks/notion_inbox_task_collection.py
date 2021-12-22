"""A inbox task collection on Notion-side."""
from dataclasses import dataclass

from domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from domain.timestamp import Timestamp
from models.framework import NotionEntity, BAD_NOTION_ID


@dataclass(frozen=True)
class NotionInboxTaskCollection(NotionEntity[InboxTaskCollection]):
    """A inbox task collection on Notion-side."""

    @staticmethod
    def new_notion_row(aggregate_root: InboxTaskCollection) -> 'NotionInboxTaskCollection':
        """Construct a new Notion row from a given aggregate root."""
        return NotionInboxTaskCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id)

    def join_with_aggregate_root(self, aggregate_root: InboxTaskCollection) -> 'NotionInboxTaskCollection':
        """Add to this Notion row from a given aggregate root."""
        return NotionInboxTaskCollection(
            notion_id=self.notion_id,
            ref_id=aggregate_root.ref_id)

    def apply_to_aggregate_root(
            self, aggregate_root: InboxTaskCollection, modification_time: Timestamp) -> InboxTaskCollection:
        """Obtain the aggregate root form of this, with a possible error."""
        return aggregate_root

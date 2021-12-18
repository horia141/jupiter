"""A recurring task collection on Notion-side."""
from dataclasses import dataclass

from domain.recurring_tasks.recurring_task_collection import RecurringTaskCollection
from domain.timestamp import Timestamp
from models.framework import NotionEntity, BAD_NOTION_ID


@dataclass()
class NotionRecurringTaskCollection(NotionEntity[RecurringTaskCollection]):
    """A recurring task collection on Notion-side."""

    @staticmethod
    def new_notion_row(aggregate_root: RecurringTaskCollection) -> 'NotionRecurringTaskCollection':
        """Construct a new Notion row from a given aggregate root."""
        return NotionRecurringTaskCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id)

    def join_with_aggregate_root(self, aggregate_root: RecurringTaskCollection) -> 'NotionRecurringTaskCollection':
        """Add to this Notion row from a given aggregate root."""
        return NotionRecurringTaskCollection(
            notion_id=self.notion_id,
            ref_id=aggregate_root.ref_id)

    def apply_to_aggregate_root(
            self, aggregate_root: RecurringTaskCollection, modification_time: Timestamp) -> RecurringTaskCollection:
        """Obtain the aggregate root form of this, with a possible error."""
        return aggregate_root

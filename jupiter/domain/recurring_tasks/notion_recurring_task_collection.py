"""A recurring task collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.recurring_tasks.recurring_task_collection import RecurringTaskCollection
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.notion import NotionEntity
from jupiter.framework.base.notion_id import BAD_NOTION_ID


@dataclass(frozen=True)
class NotionRecurringTaskCollection(NotionEntity[RecurringTaskCollection]):
    """A recurring task collection on Notion-side."""

    @staticmethod
    def new_notion_row(aggregate_root: RecurringTaskCollection) -> 'NotionRecurringTaskCollection':
        """Construct a new Notion row from a given aggregate root."""
        return NotionRecurringTaskCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id)

    def apply_to_aggregate_root(
            self, aggregate_root: RecurringTaskCollection, modification_time: Timestamp) -> RecurringTaskCollection:
        """Obtain the aggregate root form of this, with a possible error."""
        return aggregate_root

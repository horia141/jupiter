"""A smart list collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.notion import NotionEntity
from jupiter.framework.base.notion_id import BAD_NOTION_ID


@dataclass(frozen=True)
class NotionSmartListCollection(NotionEntity[SmartListCollection]):
    """A smart list collection on Notion-side."""

    @staticmethod
    def new_notion_row(aggregate_root: SmartListCollection) -> 'NotionSmartListCollection':
        """Construct a new Notion row from a given aggregate root."""
        return NotionSmartListCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id)

    def apply_to_aggregate_root(
            self, aggregate_root: SmartListCollection, modification_time: Timestamp) -> SmartListCollection:
        """Obtain the aggregate root form of this, with a possible error."""
        return aggregate_root

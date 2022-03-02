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
    def new_notion_row(entity: SmartListCollection) -> 'NotionSmartListCollection':
        """Construct a new Notion row from a given entity."""
        return NotionSmartListCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id)

    def apply_to_entity(
            self, entity: SmartListCollection, modification_time: Timestamp) -> SmartListCollection:
        """Obtain the entity form of this, with a possible error."""
        return entity

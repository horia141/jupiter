"""A smart list collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.notion import NotionTrunkEntity


@dataclass(frozen=True)
class NotionSmartListCollection(NotionTrunkEntity[SmartListCollection]):
    """A smart list collection on Notion-side."""

    @staticmethod
    def new_notion_entity(entity: SmartListCollection) -> 'NotionSmartListCollection':
        """Construct a new Notion row from a given entity."""
        return NotionSmartListCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id)

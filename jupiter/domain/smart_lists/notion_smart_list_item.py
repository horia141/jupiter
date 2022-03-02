"""A smart list item on Notion-side."""
from dataclasses import dataclass
from typing import Optional, List, Dict

from jupiter.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.domain.url import URL
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionRow
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionSmartListItem(
        NotionRow[SmartListItem, 'NotionSmartListItem.DirectInfo', 'NotionSmartListItem.InverseInfo']):
    """A smart list item on Notion-side."""

    @dataclass(frozen=True)
    class DirectInfo:
        """Extra info for the app to Notion copy."""
        tags_by_ref_id: Dict[EntityId, SmartListTag]

    @dataclass(frozen=True)
    class InverseInfo:
        """Extra info for the Notion to app copy."""
        smart_list_ref_id: EntityId
        tags_by_name: Dict[SmartListTagName, SmartListTag]

    name: str
    is_done: bool
    tags: List[str]
    url: Optional[str]

    @staticmethod
    def new_notion_row(entity: SmartListItem, extra_info: DirectInfo) -> 'NotionSmartListItem':
        """Construct a new Notion row from a given smart list item."""
        return NotionSmartListItem(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            last_edited_time=entity.last_modified_time,
            archived=entity.archived,
            name=str(entity.name),
            is_done=entity.is_done,
            tags=[str(extra_info.tags_by_ref_id[t].tag_name) for t in entity.tags_ref_id],
            url=str(entity.url))

    def new_entity(self, extra_info: InverseInfo) -> SmartListItem:
        """Create a new smart list item from this."""
        return SmartListItem.new_smart_list_item(
            archived=self.archived,
            smart_list_ref_id=extra_info.smart_list_ref_id,
            name=SmartListItemName.from_raw(self.name),
            is_done=self.is_done,
            tags_ref_id=[extra_info.tags_by_name[SmartListTagName.from_raw(t)].ref_id for t in self.tags],
            url=URL.from_raw(self.url) if self.url else None,
            source=EventSource.NOTION,
            created_time=self.last_edited_time)

    def apply_to_entity(self, entity: SmartListItem, extra_info: InverseInfo) -> SmartListItem:
        """Apply to an already existing smart list item."""
        return entity \
            .update(
                name=UpdateAction.change_to(SmartListItemName.from_raw(self.name)),
                is_done=UpdateAction.change_to(self.is_done),
                tags_ref_id=
                UpdateAction.change_to(
                    [extra_info.tags_by_name[SmartListTagName.from_raw(t)].ref_id for t in self.tags]),
                url=UpdateAction.change_to(URL.from_raw(self.url) if self.url else None),
                source=EventSource.NOTION,
                modification_time=self.last_edited_time) \
            .change_archived(
                archived=self.archived, source=EventSource.NOTION, archived_time=self.last_edited_time)

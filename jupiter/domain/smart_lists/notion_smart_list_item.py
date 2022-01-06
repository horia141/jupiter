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
from jupiter.framework.notion import NotionRow
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionSmartListItem(
        NotionRow[SmartListItem, 'NotionSmartListItem.DirectExtraInfo', 'NotionSmartListItem.InverseExtraInfo']):
    """A smart list item on Notion-side."""

    @dataclass(frozen=True)
    class DirectExtraInfo:
        """Extra info for the app to Notion copy."""
        tags_by_ref_id: Dict[EntityId, SmartListTag]

    @dataclass(frozen=True)
    class InverseExtraInfo:
        """Extra info for the Notion to app copy."""
        smart_list_ref_id: EntityId
        tags_by_name: Dict[SmartListTagName, SmartListTag]

    name: str
    is_done: bool
    tags: List[str]
    url: Optional[str]

    @staticmethod
    def new_notion_row(aggregate_root: SmartListItem, extra_info: DirectExtraInfo) -> 'NotionSmartListItem':
        """Construct a new Notion row from a given smart list item."""
        return NotionSmartListItem(
            notion_id=BAD_NOTION_ID,
            ref_id=str(aggregate_root.ref_id),
            last_edited_time=aggregate_root.last_modified_time,
            archived=aggregate_root.archived,
            name=str(aggregate_root.name),
            is_done=aggregate_root.is_done,
            tags=[str(extra_info.tags_by_ref_id[t].tag_name) for t in aggregate_root.tags_ref_id],
            url=str(aggregate_root.url))

    def new_aggregate_root(self, extra_info: InverseExtraInfo) -> SmartListItem:
        """Create a new smart list item from this."""
        return SmartListItem.new_smart_list_item(
            archived=self.archived,
            smart_list_ref_id=extra_info.smart_list_ref_id,
            name=SmartListItemName.from_raw(self.name),
            is_done=self.is_done,
            tags_ref_id=[extra_info.tags_by_name[SmartListTagName.from_raw(t)].ref_id for t in self.tags],
            url=URL.from_raw(self.url) if self.url else None,
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: SmartListItem, extra_info: InverseExtraInfo) -> SmartListItem:
        """Apply to an already existing smart list item."""
        aggregate_root.update(
            name=UpdateAction.change_to(SmartListItemName.from_raw(self.name)),
            is_done=UpdateAction.change_to(self.is_done),
            tags_ref_id=
            UpdateAction.change_to([extra_info.tags_by_name[SmartListTagName.from_raw(t)].ref_id for t in self.tags]),
            url=UpdateAction.change_to(URL.from_raw(self.url) if self.url else None),
            modification_time=self.last_edited_time)
        aggregate_root.change_archived(self.archived, self.last_edited_time)
        return aggregate_root

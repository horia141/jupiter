"""A smart list tag on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.notion import NotionRow
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionSmartListTag(NotionRow[SmartListTag, None, 'NotionSmartListTag.InverseExtraInfo']):
    """A smart list tag on Notion-side."""

    @dataclass(frozen=True)
    class InverseExtraInfo:
        """Extra info for the Notion to app copy."""
        smart_list_ref_id: EntityId

    name: str

    @staticmethod
    def new_notion_row(aggregate_root: SmartListTag, extra_info: None) -> 'NotionSmartListTag':
        """Construct a new Notion row from a given smart list tag."""
        return NotionSmartListTag(
            notion_id=BAD_NOTION_ID,
            ref_id=str(aggregate_root.ref_id),
            archived=aggregate_root.archived,
            last_edited_time=aggregate_root.last_modified_time,
            name=str(aggregate_root.tag_name))

    def new_aggregate_root(self, extra_info: InverseExtraInfo) -> SmartListTag:
        """Create a new smart list tag from this."""
        return SmartListTag.new_smart_list_tag(
            smart_list_ref_id=extra_info.smart_list_ref_id,
            tag_name=SmartListTagName.from_raw(self.name),
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: SmartListTag, extra_info: InverseExtraInfo) -> SmartListTag:
        """Apply to an already existing smart list tag."""
        aggregate_root.update(UpdateAction.change_to(SmartListTagName.from_raw(self.name)), self.last_edited_time)
        return aggregate_root

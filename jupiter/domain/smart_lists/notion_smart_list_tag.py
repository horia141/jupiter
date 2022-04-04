"""A smart list tag on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.event import EventSource
from jupiter.framework.notion import (
    NotionLeafApplyToEntityResult,
    NotionBranchTagEntity,
)
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionSmartListTag(NotionBranchTagEntity[SmartListTag]):
    """A smart list tag on Notion-side."""

    name: str

    @staticmethod
    def new_notion_entity(entity: SmartListTag) -> "NotionSmartListTag":
        """Construct a new Notion row from a given smart list tag."""
        return NotionSmartListTag(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            archived=entity.archived,
            last_edited_time=entity.last_modified_time,
            name=str(entity.tag_name),
        )

    def new_entity(self, parent_ref_id: EntityId) -> SmartListTag:
        """Create a new smart list tag from this."""
        return SmartListTag.new_smart_list_tag(
            smart_list_ref_id=parent_ref_id,
            tag_name=SmartListTagName.from_raw(self.name),
            source=EventSource.NOTION,
            created_time=self.last_edited_time,
        )

    def apply_to_entity(
        self, entity: SmartListTag
    ) -> NotionLeafApplyToEntityResult[SmartListTag]:
        """Apply to an already existing smart list tag."""
        smart_list_tag_name = SmartListTagName.from_raw(self.name)
        return NotionLeafApplyToEntityResult.just(
            entity.update(
                tag_name=UpdateAction.change_to(smart_list_tag_name),
                source=EventSource.NOTION,
                modification_time=self.last_edited_time
                if smart_list_tag_name != entity.tag_name
                else entity.last_modified_time,
            )
        )

    @property
    def nice_name(self) -> str:
        """A nice name for the Notion-side entity."""
        return self.name

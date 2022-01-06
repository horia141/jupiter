"""A smart list on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_name import SmartListName
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.notion import NotionEntity
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionSmartList(NotionEntity[SmartList]):
    """A smart list on Notion-side."""

    name: str

    @staticmethod
    def new_notion_row(aggregate_root: SmartList) -> 'NotionSmartList':
        """Construct a new Notion row from a given aggregate root."""
        return NotionSmartList(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id,
            name=str(aggregate_root.name))

    def apply_to_aggregate_root(self, aggregate_root: SmartList, modification_time: Timestamp) -> SmartList:
        """Obtain the aggregate root form of this, with a possible error."""
        smart_list_name = SmartListName.from_raw(self.name)
        aggregate_root.update(UpdateAction.change_to(smart_list_name), modification_time)
        return aggregate_root

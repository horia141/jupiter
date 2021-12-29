"""A smart list on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.entity_name import EntityName
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.notion import NotionEntity
from jupiter.framework.base.notion_id import BAD_NOTION_ID


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
        workspace_name = EntityName.from_raw(self.name)
        aggregate_root.change_name(workspace_name, modification_time)
        return aggregate_root
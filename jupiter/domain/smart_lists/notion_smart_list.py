"""A smart list on Notion-side."""
import logging
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.entity_icon import EntityIcon
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_name import SmartListName
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionEntity
from jupiter.framework.update_action import UpdateAction

LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True)
class NotionSmartList(NotionEntity[SmartList]):
    """A smart list on Notion-side."""

    name: str
    icon: Optional[str]

    @staticmethod
    def new_notion_row(aggregate_root: SmartList) -> 'NotionSmartList':
        """Construct a new Notion row from a given aggregate root."""
        return NotionSmartList(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id,
            name=str(aggregate_root.name),
            icon=aggregate_root.icon.to_safe() if aggregate_root.icon else None)

    def apply_to_aggregate_root(self, aggregate_root: SmartList, modification_time: Timestamp) -> SmartList:
        """Obtain the aggregate root form of this, with a possible error."""
        LOGGER.info(self)
        name = SmartListName.from_raw(self.name)
        icon = EntityIcon.from_safe(self.icon) if self.icon else None
        return aggregate_root.update(
            name=UpdateAction.change_to(name),
            icon=UpdateAction.change_to(icon),
            source=EventSource.NOTION,
            modification_time=
            modification_time
            if (name != aggregate_root.name or icon != aggregate_root.icon)
            else aggregate_root.last_modified_time)

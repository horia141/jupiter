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
    def new_notion_row(entity: SmartList) -> 'NotionSmartList':
        """Construct a new Notion row from a given entity."""
        return NotionSmartList(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            name=str(entity.name),
            icon=entity.icon.to_safe() if entity.icon else None)

    def apply_to_entity(self, entity: SmartList, modification_time: Timestamp) -> SmartList:
        """Obtain the entity form of this, with a possible error."""
        LOGGER.info(self)
        name = SmartListName.from_raw(self.name)
        icon = EntityIcon.from_safe(self.icon) if self.icon else None
        return entity.update(
            name=UpdateAction.change_to(name),
            icon=UpdateAction.change_to(icon),
            source=EventSource.NOTION,
            modification_time=
            modification_time
            if (name != entity.name or icon != entity.icon)
            else entity.last_modified_time)

"""A chore collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.chores.chore_collection import ChoreCollection
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.notion import NotionEntity
from jupiter.framework.base.notion_id import BAD_NOTION_ID


@dataclass(frozen=True)
class NotionChoreCollection(NotionEntity[ChoreCollection]):
    """A chore collection on Notion-side."""

    @staticmethod
    def new_notion_row(entity: ChoreCollection) -> 'NotionChoreCollection':
        """Construct a new Notion row from a given entity."""
        return NotionChoreCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id)

    def apply_to_entity(
            self, entity: ChoreCollection, modification_time: Timestamp) -> ChoreCollection:
        """Obtain the entity form of this, with a possible error."""
        return entity

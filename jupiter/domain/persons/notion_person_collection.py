"""A person collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.persons.person_collection import PersonCollection
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.notion import NotionEntity
from jupiter.framework.base.notion_id import BAD_NOTION_ID


@dataclass(frozen=True)
class NotionPersonCollection(NotionEntity[PersonCollection]):
    """A person collection on Notion-side."""

    @staticmethod
    def new_notion_row(entity: PersonCollection) -> 'NotionPersonCollection':
        """Construct a new Notion row from a given entity."""
        return NotionPersonCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id)

    def apply_to_entity(
            self, entity: PersonCollection, modification_time: Timestamp) -> PersonCollection:
        """Obtain the entity form of this, with a possible error."""
        return entity

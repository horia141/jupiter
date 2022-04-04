"""A person collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.persons.person_collection import PersonCollection
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.notion import NotionTrunkEntity


@dataclass(frozen=True)
class NotionPersonCollection(NotionTrunkEntity[PersonCollection]):
    """A person collection on Notion-side."""

    @staticmethod
    def new_notion_entity(entity: PersonCollection) -> "NotionPersonCollection":
        """Construct a new Notion row from a given entity."""
        return NotionPersonCollection(notion_id=BAD_NOTION_ID, ref_id=entity.ref_id)

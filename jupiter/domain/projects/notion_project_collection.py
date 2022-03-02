"""A project collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.projects.project_collection import ProjectCollection
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.notion import NotionEntity
from jupiter.framework.base.notion_id import BAD_NOTION_ID


@dataclass(frozen=True)
class NotionProjectCollection(NotionEntity[ProjectCollection]):
    """A project collection on Notion-side."""

    @staticmethod
    def new_notion_row(entity: ProjectCollection) -> 'NotionProjectCollection':
        """Construct a new Notion row from a given entity."""
        return NotionProjectCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id)

    def apply_to_entity(
            self, entity: ProjectCollection, modification_time: Timestamp) -> ProjectCollection:
        """Obtain the entity form of this, with a possible error."""
        return entity

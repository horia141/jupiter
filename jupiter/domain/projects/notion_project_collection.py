"""A project collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.projects.project_collection import ProjectCollection
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.notion import NotionTrunkEntity


@dataclass(frozen=True)
class NotionProjectCollection(NotionTrunkEntity[ProjectCollection]):
    """A project collection on Notion-side."""

    @staticmethod
    def new_notion_entity(entity: ProjectCollection) -> 'NotionProjectCollection':
        """Construct a new Notion row from a given entity."""
        return NotionProjectCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id)

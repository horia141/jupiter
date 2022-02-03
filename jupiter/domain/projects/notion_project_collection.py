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
    def new_notion_row(aggregate_root: ProjectCollection) -> 'NotionProjectCollection':
        """Construct a new Notion row from a given aggregate root."""
        return NotionProjectCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id)

    def apply_to_aggregate_root(
            self, aggregate_root: ProjectCollection, modification_time: Timestamp) -> ProjectCollection:
        """Obtain the aggregate root form of this, with a possible error."""
        return aggregate_root

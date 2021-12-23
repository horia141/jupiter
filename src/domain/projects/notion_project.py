"""A project on Notion-side."""
from dataclasses import dataclass

from domain.entity_name import EntityName
from domain.projects.project import Project
from domain.timestamp import Timestamp
from framework.notion import NotionEntity, BAD_NOTION_ID


@dataclass(frozen=True)
class NotionProject(NotionEntity[Project]):
    """A project on Notion-side."""

    name: str

    @staticmethod
    def new_notion_row(aggregate_root: Project) -> 'NotionProject':
        """Construct a Notion row from the Project."""
        return NotionProject(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id,
            name=str(aggregate_root.name))

    def join_with_aggregate_root(self, aggregate_root: Project) -> 'NotionProject':
        """Apply a project to an existing Notion row."""
        return NotionProject(
            notion_id=self.notion_id,
            ref_id=aggregate_root.ref_id,
            name=str(aggregate_root.name))

    def apply_to_aggregate_root(self, aggregate_root: Project, modification_time: Timestamp) -> 'Project':
        """Apply an existing Notion row to a project."""
        project_name = EntityName.from_raw(self.name)
        aggregate_root.change_name(project_name, modification_time)
        return aggregate_root

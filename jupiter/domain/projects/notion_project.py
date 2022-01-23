"""A project on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_name import ProjectName
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionEntity
from jupiter.framework.update_action import UpdateAction


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

    def apply_to_aggregate_root(self, aggregate_root: Project, modification_time: Timestamp) -> 'Project':
        """Apply an existing Notion row to a project."""
        project_name = ProjectName.from_raw(self.name)
        return aggregate_root.update(
            name=UpdateAction.change_to(project_name),
            source=EventSource.NOTION,
            modification_time=
            modification_time if project_name != aggregate_root.name else aggregate_root.last_modified_time)

"""A project on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.projects.project_name import ProjectName
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionRow
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionProject(NotionRow[Project, 'NotionProject.DirectInfo', 'NotionProject.InverseInfo']):
    """A project on Notion-side."""

    @dataclass(frozen=True)
    class DirectInfo:
        """Info when copying from the app to Notion."""

    @dataclass(frozen=True)
    class InverseInfo:
        """Extra info for the Notion to app sync."""
        project_collection_ref_id: EntityId

    key: str
    name: str

    @staticmethod
    def new_notion_row(entity: Project, extra_info: DirectInfo) -> 'NotionProject':
        """Construct a Notion row from the Project."""
        return NotionProject(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            last_edited_time=entity.last_modified_time,
            archived=entity.archived,
            key=str(entity.key),
            name=str(entity.name))

    def new_entity(self, extra_info: InverseInfo) -> Project:
        """Create a new project from this."""
        key = ProjectKey.from_raw(self.key)
        name = ProjectName.from_raw(self.name)

        return Project.new_project(
            project_collection_ref_id=extra_info.project_collection_ref_id,
            key=key,
            name=name,
            source=EventSource.NOTION,
            created_time=self.last_edited_time)

    def apply_to_entity(self, entity: Project, extra_info: InverseInfo) -> 'Project':
        """Apply an existing Notion row to a project."""
        name = ProjectName.from_raw(self.name)

        return entity.update(
            name=UpdateAction.change_to(name),
            source=EventSource.NOTION,
            modification_time=self.last_edited_time)

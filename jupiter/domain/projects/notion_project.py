"""A project on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.projects.project_name import ProjectName
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionLeafEntity, NotionLeafApplyToEntityResult
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionProject(NotionLeafEntity[Project, None, None]):
    """A project on Notion-side."""

    key: str
    name: str

    @staticmethod
    def new_notion_entity(entity: Project, extra_info: None) -> "NotionProject":
        """Construct a Notion row from the Project."""
        return NotionProject(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            last_edited_time=entity.last_modified_time,
            archived=entity.archived,
            key=str(entity.key),
            name=str(entity.name),
        )

    def new_entity(self, parent_ref_id: EntityId, extra_info: None) -> Project:
        """Create a new project from this."""
        key = ProjectKey.from_raw(self.key)
        name = ProjectName.from_raw(self.name)

        return Project.new_project(
            project_collection_ref_id=parent_ref_id,
            key=key,
            name=name,
            source=EventSource.NOTION,
            created_time=self.last_edited_time,
        )

    def apply_to_entity(
        self, entity: Project, extra_info: None
    ) -> NotionLeafApplyToEntityResult[Project]:
        """Apply an existing Notion row to a project."""
        name = ProjectName.from_raw(self.name)

        return NotionLeafApplyToEntityResult.just(
            entity.update(
                name=UpdateAction.change_to(name),
                source=EventSource.NOTION,
                modification_time=self.last_edited_time,
            )
        )

    @property
    def nice_name(self) -> str:
        """A nice name for the Notion-side entity."""
        return self.name

"""The project."""
import uuid
from dataclasses import dataclass

from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.projects.project_name import ProjectName
from jupiter.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.entity import Entity, FIRST_VERSION, LeafEntity
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class Project(LeafEntity):
    """The project."""

    @dataclass(frozen=True)
    class Created(Entity.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(Entity.Updated):
        """Updated event."""

    project_collection_ref_id: EntityId
    key: ProjectKey
    name: ProjectName
    notion_link_uuid: uuid.UUID

    @staticmethod
    def new_project(
        project_collection_ref_id: EntityId,
        key: ProjectKey,
        name: ProjectName,
        source: EventSource,
        created_time: Timestamp,
    ) -> "Project":
        """Create a project."""
        notion_link_uuid = uuid.uuid4()
        project = Project(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                Project.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                    notion_link_uuid=notion_link_uuid,
                )
            ],
            project_collection_ref_id=project_collection_ref_id,
            key=key,
            name=name,
            notion_link_uuid=notion_link_uuid,
        )
        return project

    def update(
        self,
        name: UpdateAction[ProjectName],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Project":
        """Change the project."""
        return self._new_version(
            name=name.or_else(self.name),
            new_event=Project.Updated.make_event_from_frame_args(
                source, self.version, modification_time
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.project_collection_ref_id

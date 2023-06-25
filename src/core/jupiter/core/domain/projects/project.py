"""The project."""
from dataclasses import dataclass

from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, LeafEntity
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class Project(LeafEntity):
    """The project."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class Updated(Entity.Updated):
        """Updated event."""

    project_collection_ref_id: EntityId
    name: ProjectName

    @staticmethod
    def new_project(
        project_collection_ref_id: EntityId,
        name: ProjectName,
        source: EventSource,
        created_time: Timestamp,
    ) -> "Project":
        """Create a project."""
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
                ),
            ],
            project_collection_ref_id=project_collection_ref_id,
            name=name,
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
                source,
                self.version,
                modification_time,
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.project_collection_ref_id

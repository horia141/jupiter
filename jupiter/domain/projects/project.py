"""The project."""
from dataclasses import dataclass

from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.projects.project_name import ProjectName
from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction


@dataclass()
class Project(AggregateRoot):
    """The project."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(AggregateRoot.Updated):
        """Updated event."""

    key: ProjectKey
    name: ProjectName

    @staticmethod
    def new_project(key: ProjectKey, name: ProjectName, source: EventSource, created_time: Timestamp) -> 'Project':
        """Create a project."""
        project = Project(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[],
            key=key,
            name=name)
        project.record_event(Project.Created.make_event_from_frame_args(source, project.version, created_time))
        return project

    def update(self, name: UpdateAction[ProjectName], source: EventSource, modification_time: Timestamp) -> 'Project':
        """Change the project."""
        self.name = name.or_else(self.name)
        self.record_event(
            Project.Updated.make_event_from_frame_args(source, self.version, modification_time))
        return self

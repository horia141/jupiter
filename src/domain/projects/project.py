"""The project."""
from dataclasses import dataclass

from domain.entity_name import EntityName
from domain.projects.project_key import ProjectKey
from framework.aggregate_root import AggregateRoot
from framework.base.entity_id import BAD_REF_ID
from framework.base.timestamp import Timestamp


@dataclass()
class Project(AggregateRoot):
    """The project."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(AggregateRoot.Updated):
        """Updated event."""

    _key: ProjectKey
    _name: EntityName

    @staticmethod
    def new_project(key: ProjectKey, name: EntityName, created_time: Timestamp) -> 'Project':
        """Create a project."""
        project = Project(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _key=key,
            _name=name)
        project.record_event(Project.Created.make_event_from_frame_args(created_time))
        return project

    def change_name(self, name: EntityName, modification_time: Timestamp) -> 'Project':
        """Change the name of the workspace."""
        self._name = name
        self.record_event(
            Project.Updated.make_event_from_frame_args(modification_time))
        return self

    @property
    def key(self) -> ProjectKey:
        """The key of the project."""
        return self._key

    @property
    def name(self) -> EntityName:
        """The name of the project."""
        return self._name

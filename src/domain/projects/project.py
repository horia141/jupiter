"""The project."""
from dataclasses import dataclass, field

from domain.entity_name import EntityName
from domain.projects.project_key import ProjectKey
from framework.base.timestamp import Timestamp
from framework.update_action import UpdateAction
from framework.aggregate_root import AggregateRoot
from framework.base.entity_id import BAD_REF_ID
from framework.event import Event


@dataclass()
class Project(AggregateRoot):
    """The project."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""
        key: ProjectKey
        name: EntityName

    @dataclass(frozen=True)
    class Updated(Event):
        """Updated event."""
        name: UpdateAction[EntityName] = field(default_factory=UpdateAction.do_nothing)

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
        project.record_event(Project.Created(
            key=key, name=name, timestamp=created_time))
        return project

    def change_name(self, name: EntityName, modification_time: Timestamp) -> 'Project':
        """Change the name of the workspace."""
        self._name = name
        self.record_event(
            Project.Updated(name=UpdateAction.change_to(name), timestamp=modification_time))
        return self

    @property
    def key(self) -> ProjectKey:
        """The key of the project."""
        return self._key

    @property
    def name(self) -> EntityName:
        """The name of the project."""
        return self._name

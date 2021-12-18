"""The workspace where everything happens."""
from dataclasses import dataclass, field

from domain.entity_name import EntityName
from domain.timestamp import Timestamp
from domain.timezone import Timezone
from models.framework import AggregateRoot, EntityId, Event, UpdateAction


@dataclass()
class Workspace(AggregateRoot):
    """The workspace where everything happens."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""
        name: EntityName
        timezone: Timezone
        default_project_ref_id: EntityId

    @dataclass(frozen=True)
    class Updated(Event):
        """Updated event."""
        name: UpdateAction[EntityName] = field(default_factory=UpdateAction.do_nothing)
        timezone: UpdateAction[Timezone] = field(default_factory=UpdateAction.do_nothing)
        default_project_ref_id: UpdateAction[EntityId] = field(default_factory=UpdateAction.do_nothing)

    _name: EntityName
    _timezone: Timezone
    _default_project_ref_id: EntityId

    @staticmethod
    def new_workspace(
            name: EntityName, timezone: Timezone, default_project_ref_id: EntityId,
            created_time: Timestamp) -> 'Workspace':
        """Create a new workspace."""
        workspace = Workspace(
            _ref_id=EntityId.from_raw('0'),
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _name=name,
            _timezone=timezone,
            _default_project_ref_id=default_project_ref_id)
        workspace.record_event(Workspace.Created(
            name=name, timezone=timezone, default_project_ref_id=default_project_ref_id, timestamp=created_time))
        return workspace

    def change_name(self, name: EntityName, modification_time: Timestamp) -> 'Workspace':
        """Change the name of the workspace."""
        self._name = name
        self.record_event(
            Workspace.Updated(name=UpdateAction.change_to(name), timestamp=modification_time))
        return self

    def change_timezone(self, timezone: Timezone, modification_time: Timestamp) -> 'Workspace':
        """Change the timezone of the workspace."""
        self._timezone = timezone
        self.record_event(
            Workspace.Updated(timezone=UpdateAction.change_to(timezone), timestamp=modification_time))
        return self

    def change_default_project(self, default_project_ref_id: EntityId, modification_time: Timestamp) -> 'Workspace':
        """Change the default project of the workspace."""
        self._default_project_ref_id = default_project_ref_id
        self.record_event(
            Workspace.Updated(
                default_project_ref_id=UpdateAction.change_to(default_project_ref_id), timestamp=modification_time))
        return self

    @property
    def name(self) -> EntityName:
        """The name of the workspace."""
        return self._name

    @property
    def timezone(self) -> Timezone:
        """The timezone of the workspace."""
        return self._timezone

    @property
    def default_project_ref_id(self) -> EntityId:
        """The default project of the workspace."""
        return self._default_project_ref_id

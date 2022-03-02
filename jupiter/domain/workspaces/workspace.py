"""The workspace where everything happens."""
from dataclasses import dataclass

from jupiter.domain.timezone import Timezone
from jupiter.domain.workspaces.workspace_name import WorkspaceName
from jupiter.framework.entity import Entity, FIRST_VERSION
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class Workspace(Entity):
    """The workspace where everything happens."""

    @dataclass(frozen=True)
    class Created(Entity.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(Entity.Updated):
        """Updated event."""

    @dataclass(frozen=True)
    class ChangedDefaultProject(Entity.Updated):
        """Change the default project."""

    name: WorkspaceName
    timezone: Timezone
    default_project_ref_id: EntityId

    @staticmethod
    def new_workspace(
            name: WorkspaceName, timezone: Timezone, source: EventSource, created_time: Timestamp) -> 'Workspace':
        """Create a new workspace."""
        workspace = Workspace(
            ref_id=EntityId.from_raw('0'),
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[Workspace.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            name=name,
            timezone=timezone,
            default_project_ref_id=BAD_REF_ID)
        return workspace

    def update(
            self, name: UpdateAction[WorkspaceName], timezone: UpdateAction[Timezone],
            source: EventSource, modification_time: Timestamp) -> 'Workspace':
        """Update properties of the workspace."""
        return self._new_version(
            name=name.or_else(self.name),
            timezone=timezone.or_else(self.timezone),
            new_event=Workspace.Updated.make_event_from_frame_args(source, self.version, modification_time))

    def change_default_project(
            self, default_project_ref_id: EntityId, source: EventSource, modification_time: Timestamp) -> 'Workspace':
        """Change the default project of the workspace."""
        return self._new_version(
            default_project_ref_id=default_project_ref_id,
            new_event=
            Workspace.ChangedDefaultProject.make_event_from_frame_args(source, self.version, modification_time))

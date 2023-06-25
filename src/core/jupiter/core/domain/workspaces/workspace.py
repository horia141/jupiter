"""The workspace where everything happens."""
from dataclasses import dataclass

from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, RootEntity
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class Workspace(RootEntity):
    """The workspace where everything happens."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class Updated(Entity.Updated):
        """Updated event."""

    @dataclass
    class ChangedDefaultProject(Entity.Updated):
        """Change the default project."""

    name: WorkspaceName
    default_project_ref_id: EntityId

    @staticmethod
    def new_workspace(
        name: WorkspaceName,
        source: EventSource,
        created_time: Timestamp,
    ) -> "Workspace":
        """Create a new workspace."""
        workspace = Workspace(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                Workspace.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            name=name,
            default_project_ref_id=BAD_REF_ID,
        )
        return workspace

    def update(
        self,
        name: UpdateAction[WorkspaceName],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Workspace":
        """Update properties of the workspace."""
        return self._new_version(
            name=name.or_else(self.name),
            new_event=Workspace.Updated.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    def change_default_project(
        self,
        default_project_ref_id: EntityId,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Workspace":
        """Change the default project of the workspace."""
        return self._new_version(
            default_project_ref_id=default_project_ref_id,
            new_event=Workspace.ChangedDefaultProject.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

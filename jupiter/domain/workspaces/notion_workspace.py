"""The workspace on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.workspaces.workspace import Workspace
from jupiter.domain.workspaces.workspace_name import WorkspaceName
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionRootEntity
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionWorkspace(NotionRootEntity[Workspace]):
    """The workspace on Notion-side."""

    name: str

    @staticmethod
    def new_notion_entity(entity: Workspace) -> 'NotionWorkspace':
        """Construct a Notion workspace out of a workspace."""
        return NotionWorkspace(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            name=str(entity.name))

    def apply_to_entity(self, entity: Workspace, modification_time: Timestamp) -> 'Workspace':
        """Apply a Notion workspace to an already existing workspace."""
        workspace_name = WorkspaceName.from_raw(self.name)
        return entity.update(
            name=UpdateAction.change_to(workspace_name),
            timezone=UpdateAction.do_nothing(),
            source=EventSource.NOTION,
            modification_time=
            modification_time if workspace_name != entity.name else entity.last_modified_time)

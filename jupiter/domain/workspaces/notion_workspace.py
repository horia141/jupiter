"""The workspace on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.workspaces.workspace import Workspace
from jupiter.domain.workspaces.workspace_name import WorkspaceName
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionEntity
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionWorkspace(NotionEntity[Workspace]):
    """The workspace on Notion-side."""

    name: str

    @staticmethod
    def new_notion_row(aggregate_root: Workspace) -> 'NotionWorkspace':
        """Construct a Notion workspace out of a workspace."""
        return NotionWorkspace(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id,
            name=str(aggregate_root.name))

    def apply_to_aggregate_root(self, aggregate_root: Workspace, modification_time: Timestamp) -> 'Workspace':
        """Apply a Notion workspace to an already existing workspace."""
        return aggregate_root.update(
            name=UpdateAction.change_to(WorkspaceName.from_raw(self.name)),
            timezone=UpdateAction.do_nothing(),
            source=EventSource.NOTION,
            modification_time=modification_time)

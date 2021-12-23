"""The workspace on Notion-side."""
from dataclasses import dataclass

from domain.entity_name import EntityName
from domain.workspaces.workspace import Workspace
from framework.base.timestamp import Timestamp
from framework.notion import NotionEntity, BAD_NOTION_ID


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
        workspace_name = EntityName.from_raw(self.name)
        aggregate_root.change_name(workspace_name, modification_time)
        return aggregate_root

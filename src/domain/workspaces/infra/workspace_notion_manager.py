"""The centralised point for workspace work on Notion-side."""
import abc

from domain.workspaces.notion_workspace import NotionWorkspace
from domain.workspaces.workspace import Workspace


class WorkspaceNotionManager(abc.ABC):
    """The centralised point for workspace work on Notion-side."""

    @abc.abstractmethod
    def upsert(self, workspace: Workspace) -> NotionWorkspace:
        """Upsert the root Notion structure."""

    @abc.abstractmethod
    def save(self, notion_workspace: NotionWorkspace) -> NotionWorkspace:
        """Save the root Notion structure."""

    @abc.abstractmethod
    def load(self) -> NotionWorkspace:
        """Retrieve the workspace from Notion side."""

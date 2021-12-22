"""A repository for workspaces."""
import abc

from domain.workspaces.workspace import Workspace


class WorkspaceRepository(abc.ABC):
    """A repository for workspaces."""

    @abc.abstractmethod
    def create(self, workspace: Workspace) -> Workspace:
        """Create a workspace."""

    @abc.abstractmethod
    def save(self, workspace: Workspace) -> Workspace:
        """Save a workspace."""

    @abc.abstractmethod
    def load(self) -> Workspace:
        """Loads the workspace."""

"""A repository for workspaces."""
import abc
from typing import Optional

from jupiter.domain.workspaces.workspace import Workspace


class WorkspaceAlreadyExistsError(Exception):
    """Error raised when a workspace already exists."""


class WorkspaceNotFoundError(Exception):
    """Error raised when a workspace is not found."""


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

    @abc.abstractmethod
    def load_optional(self) -> Optional[Workspace]:
        """Loads the workspace but returns null if there isn't one."""

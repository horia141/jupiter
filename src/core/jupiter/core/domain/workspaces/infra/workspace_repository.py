"""A repository for workspaces."""
import abc

from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.repository import (
    EntityNotFoundError,
    RootEntityRepository,
)


class WorkspaceNotFoundError(EntityNotFoundError):
    """Error raised when a workspace is not found."""


class WorkspaceRepository(RootEntityRepository[Workspace], abc.ABC):
    """A repository for workspaces."""

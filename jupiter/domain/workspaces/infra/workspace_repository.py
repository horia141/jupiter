"""A repository for workspaces."""
import abc

from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.repository import RootEntityRepository, RootEntityAlreadyExistsError, RootEntityNotFoundError


class WorkspaceAlreadyExistsError(RootEntityAlreadyExistsError):
    """Error raised when a workspace already exists."""


class WorkspaceNotFoundError(RootEntityNotFoundError):
    """Error raised when a workspace is not found."""


class WorkspaceRepository(RootEntityRepository[Workspace], abc.ABC):
    """A repository for workspaces."""

"""A repository for workspaces."""
import abc
from typing import Iterable, Optional

from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    RootEntityNotFoundError,
    RootEntityRepository,
)


class WorkspaceNotFoundError(RootEntityNotFoundError):
    """Error raised when a workspace is not found."""


class WorkspaceRepository(RootEntityRepository[Workspace], abc.ABC):
    """A repository for workspaces."""

    @abc.abstractmethod
    async def find_all(
        self,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> list[Workspace]:
        """Find all workspaces matching some criteria."""

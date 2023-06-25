"""A repository of user workspace links."""
import abc

from jupiter.core.domain.user_workspace_link.user_workspace_link import (
    UserWorkspaceLink,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import RootEntityRepository


class UserWorkspaceLinkNotFoundError(Exception):
    """Error raised when a user workspace link is not found."""


class UserWorkspaceLinkRepository(RootEntityRepository[UserWorkspaceLink], abc.ABC):
    """A repository for user workspace links."""

    @abc.abstractmethod
    async def load_by_user(self, user_ref_id: EntityId) -> UserWorkspaceLink:
        """Load the user workspace link for a particular user."""

"""A repository for users."""
import abc
from typing import Iterable, Optional

from jupiter.core.domain.email_address import EmailAddress
from jupiter.core.domain.user.user import User
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    RootEntityAlreadyExistsError,
    RootEntityNotFoundError,
    RootEntityRepository,
)


class UserAlreadyExistsError(RootEntityAlreadyExistsError):
    """Error raised when a user already exists."""


class UserNotFoundError(RootEntityNotFoundError):
    """Error raised when a user does not exist."""


class UserRepository(RootEntityRepository[User], abc.ABC):
    """A repository for users."""

    @abc.abstractmethod
    async def load_by_email_address(self, email_address: EmailAddress) -> User:
        """Load a user given their email address."""

    @abc.abstractmethod
    async def find_all(
        self,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> list[User]:
        """Find all users matching some criteria."""

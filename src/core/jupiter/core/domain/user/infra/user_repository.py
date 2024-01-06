"""A repository for users."""
import abc

from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.domain.user.user import User
from jupiter.core.framework.repository import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    RootEntityRepository,
)


class UserAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a user already exists."""


class UserNotFoundError(EntityNotFoundError):
    """Error raised when a user does not exist."""


class UserRepository(RootEntityRepository[User], abc.ABC):
    """A repository for users."""

    @abc.abstractmethod
    async def load_by_email_address(self, email_address: EmailAddress) -> User:
        """Load a user given their email address."""

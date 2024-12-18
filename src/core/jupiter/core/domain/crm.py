"""A representation of the CRM domain."""
from abc import ABC, abstractmethod

from jupiter.core.domain.concept.user.user import User


class CRM(ABC):
    """A representation of the CRM domain."""

    @abstractmethod
    async def upsert_as_user(self, user: User) -> None:
        """Upsert a user in the CRM."""

"""A repository of email tasks collections."""
import abc

from jupiter.core.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    TrunkEntityAlreadyExistsError,
    TrunkEntityNotFoundError,
    TrunkEntityRepository,
)


class EmailTaskCollectionAlreadyExistsError(TrunkEntityAlreadyExistsError):
    """Error raised when an email task collection already exists."""


class EmailTaskCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when an email task collection is not found."""


class EmailTaskCollectionRepository(
    TrunkEntityRepository[EmailTaskCollection],
    abc.ABC,
):
    """A repository of email task collections."""

    @abc.abstractmethod
    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> EmailTaskCollection:
        """Retrieve an email task collection by its id."""

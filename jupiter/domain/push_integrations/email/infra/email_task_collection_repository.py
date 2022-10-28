"""A repository of email tasks collections."""
import abc

from jupiter.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.repository import (
    TrunkEntityRepository,
    TrunkEntityNotFoundError,
    TrunkEntityAlreadyExistsError,
)


class EmailTaskCollectionAlreadyExistsError(TrunkEntityAlreadyExistsError):
    """Error raised when an email task collection already exists."""


class EmailTaskCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when an email task collection is not found."""


class EmailTaskCollectionRepository(
    TrunkEntityRepository[EmailTaskCollection], abc.ABC
):
    """A repository of email task collections."""

    @abc.abstractmethod
    def load_by_id(
        self, ref_id: EntityId, allow_archived: bool = False
    ) -> EmailTaskCollection:
        """Retrieve an email task collection by its id."""

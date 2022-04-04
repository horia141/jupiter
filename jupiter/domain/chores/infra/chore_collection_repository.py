"""A repository for chore collections."""
import abc

from jupiter.domain.chores.chore_collection import ChoreCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.repository import (
    TrunkEntityRepository,
    TrunkEntityNotFoundError,
    TrunkEntityAlreadyExistsError,
)


class ChoreCollectionAlreadyExistsError(TrunkEntityAlreadyExistsError):
    """Error raised when a chore collection already exists."""


class ChoreCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when a chore collection is not found."""


class ChoreCollectionRepository(TrunkEntityRepository[ChoreCollection], abc.ABC):
    """A repository of chore collections."""

    @abc.abstractmethod
    def load_by_id(
        self, ref_id: EntityId, allow_archived: bool = False
    ) -> ChoreCollection:
        """Retrieve a chore collection by its id."""

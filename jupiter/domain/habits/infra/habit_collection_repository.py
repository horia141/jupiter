"""A repository for habit collections."""
import abc

from jupiter.domain.habits.habit_collection import HabitCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.repository import (
    TrunkEntityRepository,
    TrunkEntityNotFoundError,
    TrunkEntityAlreadyExistsError,
)


class HabitCollectionAlreadyExistsError(TrunkEntityAlreadyExistsError):
    """Error raised when a habit collection already exists."""


class HabitCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when a habit collection is not found."""


class HabitCollectionRepository(TrunkEntityRepository[HabitCollection], abc.ABC):
    """A repository of habit collections."""

    @abc.abstractmethod
    def load_by_id(
        self, ref_id: EntityId, allow_archived: bool = False
    ) -> HabitCollection:
        """Retrieve a habit collection by its id."""

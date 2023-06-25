"""A repository for habit collections."""
import abc

from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    TrunkEntityAlreadyExistsError,
    TrunkEntityNotFoundError,
    TrunkEntityRepository,
)


class HabitCollectionAlreadyExistsError(TrunkEntityAlreadyExistsError):
    """Error raised when a habit collection already exists."""


class HabitCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when a habit collection is not found."""


class HabitCollectionRepository(TrunkEntityRepository[HabitCollection], abc.ABC):
    """A repository of habit collections."""

    @abc.abstractmethod
    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> HabitCollection:
        """Retrieve a habit collection by its id."""

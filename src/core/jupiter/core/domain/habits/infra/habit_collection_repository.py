"""A repository for habit collections."""
import abc

from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class HabitCollectionRepository(TrunkEntityRepository[HabitCollection], abc.ABC):
    """A repository of habit collections."""

    @abc.abstractmethod
    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> HabitCollection:
        """Retrieve a habit collection by its id."""

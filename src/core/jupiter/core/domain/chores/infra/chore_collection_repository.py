"""A repository for chore collections."""
import abc

from jupiter.core.domain.chores.chore_collection import ChoreCollection
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class ChoreCollectionRepository(TrunkEntityRepository[ChoreCollection], abc.ABC):
    """A repository of chore collections."""

    @abc.abstractmethod
    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> ChoreCollection:
        """Retrieve a chore collection by its id."""

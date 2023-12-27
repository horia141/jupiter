"""A repository for smart list collections."""
import abc

from jupiter.core.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class SmartListCollectionRepository(
    TrunkEntityRepository[SmartListCollection],
    abc.ABC,
):
    """A repository of smart list collections."""

    @abc.abstractmethod
    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> SmartListCollection:
        """Retrieve a smart list collection by its id."""

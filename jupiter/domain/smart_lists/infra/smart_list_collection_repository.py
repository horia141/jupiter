"""A repository for smart list collections."""
import abc

from jupiter.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.repository import TrunkEntityRepository, TrunkEntityNotFoundError


class SmartListCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when a smart list collection is not found."""


class SmartListCollectionRepository(TrunkEntityRepository[SmartListCollection], abc.ABC):
    """A repository of smart list collections."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListCollection:
        """Retrieve a smart list collection by its id."""

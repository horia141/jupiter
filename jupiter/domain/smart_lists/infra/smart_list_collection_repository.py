"""A repository for smart list collections."""
import abc

from jupiter.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class SmartListCollectionNotFoundError(Exception):
    """Error raised when a smart list collection is not found."""


class SmartListCollectionRepository(Repository, abc.ABC):
    """A repository of smart list collections."""

    @abc.abstractmethod
    def create(self, smart_list_collection: SmartListCollection) -> SmartListCollection:
        """Create a smart list collection."""

    @abc.abstractmethod
    def save(self, smart_list_collection: SmartListCollection) -> SmartListCollection:
        """Save a smart list collection."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> SmartListCollection:
        """Retrieve a smart list collection by its id."""

    @abc.abstractmethod
    def load_by_workspace(self, workspace_ref_id: EntityId) -> SmartListCollection:
        """Retrieve a smart list collection by its owning project id."""

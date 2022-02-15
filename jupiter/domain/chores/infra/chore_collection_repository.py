"""A repository for chore collections."""
import abc

from jupiter.domain.chores.chore_collection import ChoreCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class ChoreCollectionNotFoundError(Exception):
    """Error raised when a chore collection is not found."""


class ChoreCollectionRepository(Repository, abc.ABC):
    """A repository of chore collections."""

    @abc.abstractmethod
    def create(self, chore_collection: ChoreCollection) -> ChoreCollection:
        """Create a chore collection."""

    @abc.abstractmethod
    def save(self, chore_collection: ChoreCollection) -> ChoreCollection:
        """Save a chore collection."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> ChoreCollection:
        """Retrieve a chore collection by its id."""

    @abc.abstractmethod
    def load_by_workspace(self, workspace_ref_id: EntityId) -> ChoreCollection:
        """Retrieve a chore collection by its owning workspace id."""

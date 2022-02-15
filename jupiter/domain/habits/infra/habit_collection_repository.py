"""A repository for habit collections."""
import abc

from jupiter.domain.habits.habit_collection import HabitCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class HabitCollectionNotFoundError(Exception):
    """Error raised when a habit collection is not found."""


class HabitCollectionRepository(Repository, abc.ABC):
    """A repository of habit collections."""

    @abc.abstractmethod
    def create(self, habit_collection: HabitCollection) -> HabitCollection:
        """Create a habit collection."""

    @abc.abstractmethod
    def save(self, habit_collection: HabitCollection) -> HabitCollection:
        """Save a habit collection."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> HabitCollection:
        """Retrieve a habit collection by its id."""

    @abc.abstractmethod
    def load_by_workspace(self, workspace_ref_id: EntityId) -> HabitCollection:
        """Retrieve a habit collection by its owning workspace id."""

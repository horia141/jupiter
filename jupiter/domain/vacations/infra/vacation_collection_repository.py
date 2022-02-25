"""A repository for vacation collections."""
import abc

from jupiter.domain.vacations.vacation_collection import VacationCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class VacationCollectionNotFoundError(Exception):
    """Error raised when a vacation collection is not found."""


class VacationCollectionRepository(Repository, abc.ABC):
    """A repository of vacation collections."""

    @abc.abstractmethod
    def create(self, vacation_collection: VacationCollection) -> VacationCollection:
        """Create a vacation collection."""

    @abc.abstractmethod
    def save(self, vacation_collection: VacationCollection) -> VacationCollection:
        """Save a vacation collection."""

    @abc.abstractmethod
    def load_by_workspace(self, workspace_ref_id: EntityId) -> VacationCollection:
        """Retrieve a vacation collection by its owning workspace id."""

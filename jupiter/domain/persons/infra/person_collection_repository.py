"""A repository of person collections."""
import abc

from jupiter.domain.persons.person_collection import PersonCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class PersonCollectionNotFoundError(Exception):
    """Error raised when the person collection is not found."""


class PersonCollectionRepository(Repository, abc.ABC):
    """A repository of person collections."""

    @abc.abstractmethod
    def create(self, person_collection: PersonCollection) -> PersonCollection:
        """Create a person collections."""

    @abc.abstractmethod
    def save(self, person_collection: PersonCollection) -> PersonCollection:
        """Save a person collections - it should already exist."""

    @abc.abstractmethod
    def load_by_workspace(self, workspace_ref_id: EntityId) -> PersonCollection:
        """Load the person collections."""

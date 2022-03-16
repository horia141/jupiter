"""A repository of person collections."""
import abc

from jupiter.domain.persons.person_collection import PersonCollection
from jupiter.framework.repository import TrunkEntityRepository, TrunkEntityNotFoundError


class PersonCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when the person collection is not found."""


class PersonCollectionRepository(TrunkEntityRepository[PersonCollection], abc.ABC):
    """A repository of person collections."""

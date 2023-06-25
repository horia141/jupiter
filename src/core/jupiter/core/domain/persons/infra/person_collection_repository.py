"""A repository of person collections."""
import abc

from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.framework.repository import (
    TrunkEntityNotFoundError,
    TrunkEntityRepository,
)


class PersonCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when the person collection is not found."""


class PersonCollectionRepository(TrunkEntityRepository[PersonCollection], abc.ABC):
    """A repository of person collections."""

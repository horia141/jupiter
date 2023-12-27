"""A repository of person collections."""
import abc

from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class PersonCollectionRepository(TrunkEntityRepository[PersonCollection], abc.ABC):
    """A repository of person collections."""

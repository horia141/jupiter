"""A repository of persons."""
import abc

from jupiter.core.domain.persons.person import Person
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class PersonRepository(LeafEntityRepository[Person], abc.ABC):
    """A repository of person."""

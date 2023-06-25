"""A repository of persons."""
import abc

from jupiter.core.domain.persons.person import Person
from jupiter.core.framework.repository import (
    LeafEntityNotFoundError,
    LeafEntityRepository,
)


class PersonAlreadyExistsError(Exception):
    """Error raised when a person already exists."""


class PersonNotFoundError(LeafEntityNotFoundError):
    """Error raised when a person is not found."""


class PersonRepository(LeafEntityRepository[Person], abc.ABC):
    """A repository of person."""

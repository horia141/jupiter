"""A repository of persons."""
import abc

from jupiter.domain.persons.person import Person
from jupiter.framework.repository import LeafEntityRepository, LeafEntityNotFoundError


class PersonAlreadyExistsError(Exception):
    """Error raised when a person already exists."""


class PersonNotFoundError(LeafEntityNotFoundError):
    """Error raised when a person is not found."""


class PersonRepository(LeafEntityRepository[Person], abc.ABC):
    """A repository of person."""

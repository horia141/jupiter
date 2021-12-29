"""A repository of persons."""
import abc
from typing import Optional, Iterable, List

from jupiter.domain.prm.person import Person
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class PersonAlreadyExistsError(Exception):
    """Error raised when a person already exists."""


class PersonNotFoundError(Exception):
    """Error raised when a person is not found."""


class PersonRepository(Repository, abc.ABC):
    """A repository of person."""

    @abc.abstractmethod
    def create(self, person: Person) -> Person:
        """Create a person."""

    @abc.abstractmethod
    def save(self, person: Person) -> Person:
        """Save a person - it should already exist."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Person:
        """Find a person by id."""

    @abc.abstractmethod
    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> List[Person]:
        """Find all person matching some criteria."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> Person:
        """Hard remove a person - an irreversible operation."""
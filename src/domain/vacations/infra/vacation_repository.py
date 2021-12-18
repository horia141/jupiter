"""A repository of vacations."""
import abc
from typing import Optional, List, Iterable

from domain.vacations.vacation import Vacation
from models.framework import Repository, EntityId


class VacationRepository(Repository, abc.ABC):
    """A repository of vacations."""

    @abc.abstractmethod
    def create(self, vacation: Vacation) -> Vacation:
        """Create a vacation."""

    @abc.abstractmethod
    def save(self, vacation: Vacation) -> Vacation:
        """Save a vacation - it should already exist."""

    @abc.abstractmethod
    def get_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Vacation:
        """Find a vacation by id."""

    @abc.abstractmethod
    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> List[Vacation]:
        """Find all vacations matching some criteria."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> None:
        """Hard remove a vacation - an irreversible operation."""

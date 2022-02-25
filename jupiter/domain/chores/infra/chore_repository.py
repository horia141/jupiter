"""A repository of chores."""
import abc
from typing import Optional, Iterable

from jupiter.domain.chores.chore import Chore
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class ChoreNotFoundError(Exception):
    """Error raised when a chore is not found."""


class ChoreRepository(Repository, abc.ABC):
    """A repository of chores."""

    @abc.abstractmethod
    def create(self, chore: Chore) -> Chore:
        """Create a chore."""

    @abc.abstractmethod
    def save(self, chore: Chore) -> Chore:
        """Save a chore - it should already exist."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Chore:
        """Load a chore by id."""

    @abc.abstractmethod
    def find_all(
            self,
            chore_collection_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[Chore]:
        """Find all chores."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> Chore:
        """Hard remove a chore - an irreversible operation."""

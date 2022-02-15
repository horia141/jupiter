"""A repository of habits."""
import abc
from typing import Optional, Iterable

from jupiter.domain.habits.habit import Habit
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class HabitNotFoundError(Exception):
    """Error raised when a habit is not found."""


class HabitRepository(Repository, abc.ABC):
    """A repository of habits."""

    @abc.abstractmethod
    def create(self, habit: Habit) -> Habit:
        """Create a habit."""

    @abc.abstractmethod
    def save(self, habit: Habit) -> Habit:
        """Save a habit - it should already exist."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Habit:
        """Load a habit by id."""

    @abc.abstractmethod
    def find_all(
            self,
            habit_collection_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[Habit]:
        """Find all habits."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> Habit:
        """Hard remove a habit - an irreversible operation."""

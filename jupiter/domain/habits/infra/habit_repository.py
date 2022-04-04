"""A repository of habits."""
import abc
from typing import Optional, Iterable

from jupiter.domain.habits.habit import Habit
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.repository import LeafEntityRepository, LeafEntityNotFoundError


class HabitNotFoundError(LeafEntityNotFoundError):
    """Error raised when a habit is not found."""


class HabitRepository(LeafEntityRepository[Habit], abc.ABC):
    """A repository of habits."""

    @abc.abstractmethod
    def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> Iterable[Habit]:
        """Find all habits."""

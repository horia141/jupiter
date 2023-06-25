"""A repository of habits."""
import abc
from typing import Iterable, Optional

from jupiter.core.domain.habits.habit import Habit
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityNotFoundError,
    LeafEntityRepository,
)


class HabitNotFoundError(LeafEntityNotFoundError):
    """Error raised when a habit is not found."""


class HabitRepository(LeafEntityRepository[Habit], abc.ABC):
    """A repository of habits."""

    @abc.abstractmethod
    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> Iterable[Habit]:
        """Find all habits."""

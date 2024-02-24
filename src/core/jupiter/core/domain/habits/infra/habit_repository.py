"""A repository of habits."""
import abc
from typing import Iterable, Optional

from jupiter.core.domain.habits.habit import Habit
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class HabitRepository(LeafEntityRepository[Habit], abc.ABC):
    """A repository of habits."""

"""A repository of chores."""
import abc
from typing import Iterable, List, Optional

from jupiter.core.domain.chores.chore import Chore
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class ChoreRepository(LeafEntityRepository[Chore], abc.ABC):
    """A repository of chores."""

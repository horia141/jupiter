"""A repository of chores."""
import abc

from jupiter.core.domain.chores.chore import Chore
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class ChoreRepository(LeafEntityRepository[Chore], abc.ABC):
    """A repository of chores."""

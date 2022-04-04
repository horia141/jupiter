"""A repository of chores."""
import abc
from typing import Optional, Iterable, List

from jupiter.domain.chores.chore import Chore
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.repository import LeafEntityRepository, LeafEntityNotFoundError


class ChoreNotFoundError(LeafEntityNotFoundError):
    """Error raised when a chore is not found."""


class ChoreRepository(LeafEntityRepository[Chore], abc.ABC):
    """A repository of chores."""

    @abc.abstractmethod
    def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Chore]:
        """Find all chores."""

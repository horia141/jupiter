"""A repository of big plans."""
import abc
from typing import Optional, Iterable, List

from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.repository import LeafEntityRepository, LeafEntityNotFoundError


class BigPlanNotFoundError(LeafEntityNotFoundError):
    """Error raised when a big plan was not found."""


class BigPlanRepository(LeafEntityRepository[BigPlan], abc.ABC):
    """A repository of big plans."""

    @abc.abstractmethod
    def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[BigPlan]:
        """Find all big plans."""

"""A repository for big plan collections."""
import abc

from jupiter.core.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class BigPlanCollectionRepository(TrunkEntityRepository[BigPlanCollection], abc.ABC):
    """A repository of big plan collections."""

    @abc.abstractmethod
    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> BigPlanCollection:
        """Retrieve a big plan collection by its id."""

"""A repository for big plan collections."""
import abc

from jupiter.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.repository import (
    TrunkEntityRepository,
    TrunkEntityNotFoundError,
    TrunkEntityAlreadyExistsError,
)


class BigPlanCollectionAlreadyExistsError(TrunkEntityAlreadyExistsError):
    """Error raised when a big plan collection already exists."""


class BigPlanCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when a big plan collection is not found."""


class BigPlanCollectionRepository(TrunkEntityRepository[BigPlanCollection], abc.ABC):
    """A repository of big plan collections."""

    @abc.abstractmethod
    def load_by_id(
        self, ref_id: EntityId, allow_archived: bool = False
    ) -> BigPlanCollection:
        """Retrieve a big plan collection by its id."""

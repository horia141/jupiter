"""A repository for big plan collections."""
import abc

from jupiter.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class BigPlanCollectionNotFoundError(Exception):
    """Error raised when a big plan collection is not found."""


class BigPlanCollectionRepository(Repository, abc.ABC):
    """A repository of big plan collections."""

    @abc.abstractmethod
    def create(self, big_plan_collection: BigPlanCollection) -> BigPlanCollection:
        """Create a big plan collection."""

    @abc.abstractmethod
    def save(self, big_plan_collection: BigPlanCollection) -> BigPlanCollection:
        """Save a big plan collection."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> BigPlanCollection:
        """Retrieve a big plan collection by its id."""

    @abc.abstractmethod
    def load_by_workspace(self, workspace_ref_id: EntityId) -> BigPlanCollection:
        """Retrieve a big plan collection by its owning project id."""

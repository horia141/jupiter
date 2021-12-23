"""A repository of big plans."""
import abc
from typing import Optional, Iterable

from domain.big_plans.big_plan import BigPlan
from domain.big_plans.big_plan_collection import BigPlanCollection
from framework.base.entity_id import EntityId
from framework.storage import Repository


class BigPlanRepository(Repository, abc.ABC):
    """A repository of big plans."""

    @abc.abstractmethod
    def create(self, big_plan_collection: BigPlanCollection, big_plan: BigPlan) -> BigPlan:
        """Create a big plan."""

    @abc.abstractmethod
    def save(self, big_plan: BigPlan) -> BigPlan:
        """Save a big plan - it should already exist."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> BigPlan:
        """Load a big plan by id."""

    @abc.abstractmethod
    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_big_plan_collection_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[BigPlan]:
        """Find all big plans."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> BigPlan:
        """Hard remove a big plan - an irreversible operation."""

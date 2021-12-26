"""A repository for big plan collections."""
import abc
from typing import Optional, Iterable

from domain.big_plans.big_plan_collection import BigPlanCollection
from framework.base.entity_id import EntityId
from framework.storage import Repository


class BigPlanCollectionAlreadyExistsError(Exception):
    """Error raised when a big plan collection already exists."""


class BigPlanCollectionNotFoundError(Exception):
    """Error raised when a big plan collection is not found."""


class BigPlanCollectionRepository(Repository, abc.ABC):
    """A repository of big plan collections."""

    @abc.abstractmethod
    def create(self, big_plan_collection: BigPlanCollection) -> BigPlanCollection:
        """Create a big plan collection."""

    @abc.abstractmethod
    def load_by_project(self, project_ref_id: EntityId) -> BigPlanCollection:
        """Retrieve a big plan collection by its owning project id."""

    @abc.abstractmethod
    def find_all(self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
                 filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[BigPlanCollection]:
        """Retrieve recurring task collections."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> BigPlanCollection:
        """Hard remove a big plan collection."""

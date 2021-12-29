"""A repository for recurring task collections."""
import abc
from typing import Optional, Iterable

from jupiter.domain.recurring_tasks.recurring_task_collection import RecurringTaskCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class RecurringTaskCollectionAlreadyExistsError(Exception):
    """Error raised when a recurring task collection with the given key already exists."""


class RecurringTaskCollectionNotFoundError(Exception):
    """Error raised when a recurring task collection is not found."""


class RecurringTaskCollectionRepository(Repository, abc.ABC):
    """A repository of recurring task collections."""

    @abc.abstractmethod
    def create(self, recurring_task_collection: RecurringTaskCollection) -> RecurringTaskCollection:
        """Create a recurring task collection."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId) -> RecurringTaskCollection:
        """Retrieve a recurring task collection by its id."""

    @abc.abstractmethod
    def load_by_project(self, project_ref_id: EntityId) -> RecurringTaskCollection:
        """Retrieve a recurring task collection by its owning project id."""

    @abc.abstractmethod
    def find_all(self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
                 filter_project_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[RecurringTaskCollection]:
        """Retrieve recurring task collections."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> RecurringTaskCollection:
        """Hard remove a recurring task collection."""

"""A repository for recurring task collections."""
import abc

from jupiter.domain.recurring_tasks.recurring_task_collection import RecurringTaskCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class RecurringTaskCollectionNotFoundError(Exception):
    """Error raised when a recurring task collection is not found."""


class RecurringTaskCollectionRepository(Repository, abc.ABC):
    """A repository of recurring task collections."""

    @abc.abstractmethod
    def create(self, recurring_task_collection: RecurringTaskCollection) -> RecurringTaskCollection:
        """Create a recurring task collection."""

    @abc.abstractmethod
    def save(self, recurring_task_collection: RecurringTaskCollection) -> RecurringTaskCollection:
        """Save a recurring task collection."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> RecurringTaskCollection:
        """Retrieve a recurring task collection by its id."""

    @abc.abstractmethod
    def load_by_workspace(self, workspace_ref_id: EntityId) -> RecurringTaskCollection:
        """Retrieve a recurring task collection by its owning workspace id."""

"""A repository for inbox task collections."""
import abc

from jupiter.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.storage import Repository


class InboxTaskCollectionNotFoundError(Exception):
    """Error raised when an inbox task collection does not exist."""


class InboxTaskCollectionRepository(Repository, abc.ABC):
    """A repository of inbox task collections."""

    @abc.abstractmethod
    def create(self, inbox_task_collection: InboxTaskCollection) -> InboxTaskCollection:
        """Create a inbox task collection."""

    @abc.abstractmethod
    def save(self, inbox_task_collection: InboxTaskCollection) -> InboxTaskCollection:
        """Save a big plan collection."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> InboxTaskCollection:
        """Retrieve a inbox task collection by its id."""

    @abc.abstractmethod
    def load_by_workspace(self, workspace_ref_id: EntityId) -> InboxTaskCollection:
        """Retrieve a inbox task collection by its owning project id."""

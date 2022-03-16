"""A repository for inbox task collections."""
import abc

from jupiter.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.repository import TrunkEntityRepository, TrunkEntityNotFoundError


class InboxTaskCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when an inbox task collection does not exist."""


class InboxTaskCollectionRepository(TrunkEntityRepository[InboxTaskCollection], abc.ABC):
    """A repository of inbox task collections."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> InboxTaskCollection:
        """Retrieve a inbox task collection by its id."""

"""A repository for inbox task collections."""
import abc

from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class InboxTaskCollectionRepository(
    TrunkEntityRepository[InboxTaskCollection],
    abc.ABC,
):
    """A repository of inbox task collections."""

    @abc.abstractmethod
    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> InboxTaskCollection:
        """Retrieve a inbox task collection by its id."""

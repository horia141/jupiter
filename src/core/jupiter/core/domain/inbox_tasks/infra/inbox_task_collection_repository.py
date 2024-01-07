"""A repository for inbox task collections."""
import abc

from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class InboxTaskCollectionRepository(
    TrunkEntityRepository[InboxTaskCollection],
    abc.ABC,
):
    """A repository of inbox task collections."""

"""A repository for gc log entries."""
import abc

from jupiter.core.domain.gc.gc_log_entry import GCLogEntry
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityNotFoundError,
    LeafEntityRepository,
)


class GCLogEntryNotFoundError(LeafEntityNotFoundError):
    """Error raised when a gc log entry is not found."""


class GCLogEntryRepository(LeafEntityRepository[GCLogEntry], abc.ABC):
    """A repository of gc log entries."""

    @abc.abstractmethod
    async def find_last(
        self,
        parent_ref_id: EntityId,
        limit: int,
    ) -> list[GCLogEntry]:
        """Find the last N GC log entries."""

"""A repository for task generation log entries."""
import abc

from jupiter.core.domain.gen.gen_log_entry import GenLogEntry
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityNotFoundError,
    LeafEntityRepository,
)


class GenLogEntryNotFoundError(LeafEntityNotFoundError):
    """Error raised when a task generation log entry is not found."""


class GenLogEntryRepository(LeafEntityRepository[GenLogEntry], abc.ABC):
    """A repository of task generation log entries."""

    @abc.abstractmethod
    async def find_last(
        self,
        parent_ref_id: EntityId,
        limit: int,
    ) -> list[GenLogEntry]:
        """Find the last N task generation log entries."""

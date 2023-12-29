"""A repository for gc logs."""
import abc

from jupiter.core.domain.gc.gc_log import GCLog
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class GCLogRepository(TrunkEntityRepository[GCLog], abc.ABC):
    """A repository of gc logs."""

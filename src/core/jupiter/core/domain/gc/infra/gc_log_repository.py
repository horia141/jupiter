"""A repository for gc logs."""
import abc

from jupiter.core.domain.gc.gc_log import GCLog
from jupiter.core.framework.repository import (
    TrunkEntityAlreadyExistsError,
    TrunkEntityNotFoundError,
    TrunkEntityRepository,
)


class GCLogAlreadyExistsError(TrunkEntityAlreadyExistsError):
    """Error raised when a gc log already exists."""


class GCLogNotFoundError(TrunkEntityNotFoundError):
    """Error raised when a gc log is not found."""


class GCLogRepository(TrunkEntityRepository[GCLog], abc.ABC):
    """A repository of gc logs."""

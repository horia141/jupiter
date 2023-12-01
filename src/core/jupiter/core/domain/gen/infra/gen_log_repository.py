"""A repository for task generation logs."""
import abc

from jupiter.core.domain.gen.gen_log import GenLog
from jupiter.core.framework.repository import (
    TrunkEntityAlreadyExistsError,
    TrunkEntityNotFoundError,
    TrunkEntityRepository,
)


class GenLogAlreadyExistsError(TrunkEntityAlreadyExistsError):
    """Error raised when a task generation log already exists."""


class GenLogNotFoundError(TrunkEntityNotFoundError):
    """Error raised when a task generation log is not found."""


class GenLogRepository(TrunkEntityRepository[GenLog], abc.ABC):
    """A repository of task generation logs."""

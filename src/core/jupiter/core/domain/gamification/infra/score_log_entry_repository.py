"""A repository for score log entries."""
import abc

from jupiter.core.domain.gamification.score_log_entry import ScoreLogEntry
from jupiter.core.framework.repository import (
    EntityAlreadyExistsError,
    LeafEntityNotFoundError,
    LeafEntityRepository,
)


class ScoreLogEntryAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a score log entry already exists."""


class ScoreLogEntryNotFoundError(LeafEntityNotFoundError):
    """Error raised when a score log entry is not found."""


class ScoreLogEntryRepository(LeafEntityRepository[ScoreLogEntry], abc.ABC):
    """A repository of score log entries."""

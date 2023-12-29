"""A repository for score log entries."""
import abc

from jupiter.core.domain.gamification.score_log_entry import ScoreLogEntry
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class ScoreLogEntryRepository(LeafEntityRepository[ScoreLogEntry], abc.ABC):
    """A repository of score log entries."""

"""A repository for score logs."""
import abc

from jupiter.core.domain.gamification.score_log import ScoreLog
from jupiter.core.framework.repository import (
    TrunkEntityAlreadyExistsError,
    TrunkEntityNotFoundError,
    TrunkEntityRepository,
)


class ScoreLogAlreadyExistsError(TrunkEntityAlreadyExistsError):
    """Error raised when a score log already exists."""


class ScoreLogNotFoundError(TrunkEntityNotFoundError):
    """Error raised when a score log is not found."""


class ScoreLogRepository(TrunkEntityRepository[ScoreLog], abc.ABC):
    """A repository of score logs."""

"""A repository for score logs."""
import abc

from jupiter.core.domain.gamification.score_log import ScoreLog
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class ScoreLogRepository(TrunkEntityRepository[ScoreLog], abc.ABC):
    """A repository of score logs."""

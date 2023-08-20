"""A repository for score stats."""
import abc
from typing import Tuple

from jupiter.core.domain.gamification.score_stats import ScoreStats
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    RecordAlreadyExistsError,
    RecordNotFoundError,
    RecordRepository,
)


class ScoreStatsAlreadyExistsError(RecordAlreadyExistsError):
    """Error raised when a score stats already exists."""


class ScoreStatsNotFoundError(RecordNotFoundError):
    """Error raised when a score stats is not found."""


class ScoreStatsRepository(
    RecordRepository[
        ScoreStats, Tuple[EntityId, RecurringTaskPeriod | None, str], EntityId
    ],
    abc.ABC,
):
    """A repository of score stats."""

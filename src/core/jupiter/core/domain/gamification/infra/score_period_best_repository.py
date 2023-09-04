"""A repository for score per-period bests."""
import abc
from typing import Tuple

from jupiter.core.domain.gamification.score_period_best import ScorePeriodBest
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    RecordAlreadyExistsError,
    RecordNotFoundError,
    RecordRepository,
)


class ScorePeriodBestAlreadyExistsError(RecordAlreadyExistsError):
    """Error raised when a score period best already exists."""


class ScorePeriodBestNotFoundError(RecordNotFoundError):
    """Error raised when a score period best is not found."""


class ScorePeriodBestRepository(
    RecordRepository[
        ScorePeriodBest,
        Tuple[EntityId, RecurringTaskPeriod | None, str, RecurringTaskPeriod],
        EntityId,
    ],
    abc.ABC,
):
    """A repository of score period bests."""

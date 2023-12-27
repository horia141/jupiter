"""A repository for score per-period bests."""
import abc
from typing import Tuple

from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.gamification.score_period_best import ScorePeriodBest
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    RecordRepository,
)


class ScorePeriodBestRepository(
    RecordRepository[
        ScorePeriodBest,
        Tuple[EntityId, RecurringTaskPeriod | None, str, RecurringTaskPeriod],
        EntityId,
    ],
    abc.ABC,
):
    """A repository of score period bests."""

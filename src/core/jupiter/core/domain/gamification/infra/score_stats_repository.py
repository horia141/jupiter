"""A repository for score stats."""
import abc
from typing import Tuple

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.gamification.score_stats import ScoreStats
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    RecordRepository,
)


class ScoreStatsRepository(
    RecordRepository[
        ScoreStats, Tuple[EntityId, RecurringTaskPeriod | None, str], EntityId
    ],
    abc.ABC,
):
    """A repository of score stats."""

    @abc.abstractmethod
    async def find_all_in_timerange(
        self,
        score_log_ref_id: EntityId,
        period: RecurringTaskPeriod,
        start_date: ADate,
        end_date: ADate,
    ) -> list[ScoreStats]:
        """Find all score stats in a given time range."""

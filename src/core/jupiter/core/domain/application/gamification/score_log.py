"""A container for all the scores a user has."""

import abc

from jupiter.core.domain.application.gamification.score_log_entry import ScoreLogEntry
from jupiter.core.domain.application.gamification.score_period_best import (
    ScorePeriodBest,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    IsRefId,
    ParentLink,
    TrunkEntity,
    create_entity_action,
    entity,
)
from jupiter.core.framework.record import ContainsRecords
from jupiter.core.framework.repository import TrunkEntityRepository


@entity
class ScoreLog(TrunkEntity):
    """a log of the scores a user receives."""

    user: ParentLink

    entries = ContainsMany(ScoreLogEntry, score_log_ref_id=IsRefId())
    period_bests = ContainsRecords(ScorePeriodBest, score_log_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_score_log(
        ctx: DomainContext,
        user_ref_id: EntityId,
    ) -> "ScoreLog":
        """Create a score log for a user."""
        return ScoreLog._create(
            ctx,
            user=ParentLink(user_ref_id),
        )


class ScoreLogRepository(TrunkEntityRepository[ScoreLog], abc.ABC):
    """A repository of score logs."""

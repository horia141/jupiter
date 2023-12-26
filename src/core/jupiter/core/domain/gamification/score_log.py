"""A container for all the scores a user has."""
from jupiter.core.domain.gamification.score_log_entry import ScoreLogEntry
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    IsRefId,
    TrunkEntity,
    create_entity_action,
    entity,
)


@entity
class ScoreLog(TrunkEntity):
    """a log of the scores a user receives."""

    user_ref_id: EntityId

    entries = ContainsMany(ScoreLogEntry, score_log_ref_id=IsRefId())
    # period_bests = ContainsMany(ScorePeriodBest, score_log_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_score_log(
        ctx: DomainContext,
        user_ref_id: EntityId,
    ) -> "ScoreLog":
        """Create a score log for a user."""
        return ScoreLog._create(
            ctx,
            user_ref_id=user_ref_id,
        )

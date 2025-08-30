"""A log of stats computation actions a user has performed."""

from jupiter.core.domain.application.stats.stats_log_entry import StatsLogEntry
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


@entity
class StatsLog(TrunkEntity):
    """A log of stats computation actions a user has performed."""

    workspace: ParentLink

    entries = ContainsMany(StatsLogEntry, stats_log_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_stats_log(ctx: DomainContext, workspace_ref_id: EntityId) -> "StatsLog":
        """Create a new stats log."""
        return StatsLog._create(ctx, workspace=ParentLink(workspace_ref_id))

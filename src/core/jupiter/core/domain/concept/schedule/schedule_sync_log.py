"""A sync log attached to a schedule domain."""
from jupiter.core.domain.concept.schedule.schedule_sync_log_entry import (
    ScheduleSyncLogEntry,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    BranchEntity,
    ContainsMany,
    IsRefId,
    ParentLink,
    create_entity_action,
    entity,
)


@entity
class ScheduleSyncLog(BranchEntity):
    """A sync log attached to a schedule domain."""

    schedule_domain: ParentLink

    entries = ContainsMany(ScheduleSyncLogEntry, sync_log_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_schedule_sync_log(
        ctx: DomainContext, schedule_domain_ref_id: EntityId
    ) -> "ScheduleSyncLog":
        """Create a new sync log."""
        return ScheduleSyncLog._create(
            ctx, schedule_domain=ParentLink(schedule_domain_ref_id)
        )

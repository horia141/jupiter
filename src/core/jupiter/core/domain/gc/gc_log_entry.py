"""A particular entry in the GC log."""

from jupiter.core.domain.entity_summary import EntitySummary
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    CrownEntity,
    LeafEntity,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.event import EventSource


@entity
class GCLogEntry(LeafEntity):
    """A particular entry in the GC log."""

    gc_log: ParentLink
    source: EventSource
    gc_targets: list[SyncTarget]
    opened: bool
    entity_records: list[EntitySummary]

    @staticmethod
    @create_entity_action
    def new_log_entry(
        ctx: DomainContext,
        gc_log_ref_id: EntityId,
        gc_targets: list[SyncTarget],
    ) -> "GCLogEntry":
        """Create a new GC log entry."""
        return GCLogEntry._create(
            ctx,
            name=GCLogEntry.build_name(gc_targets, ctx.action_timestamp),
            gc_log=ParentLink(gc_log_ref_id),
            source=ctx.event_source,
            gc_targets=gc_targets,
            opened=True,
            entity_records=[],
        )

    @staticmethod
    def build_name(gc_targets: list[SyncTarget], created_time: Timestamp) -> EntityName:
        """Build the name for a GC log entry."""
        return EntityName(
            f"GC Log Entry for {','.join(str(g) for g in gc_targets)} at {created_time}"
        )

    @update_entity_action
    def add_entity(
        self,
        ctx: DomainContext,
        entity: CrownEntity,
    ) -> "GCLogEntry":
        """Add an entity to the GC log entry."""
        if not self.opened:
            raise Exception("Can't add an entity to a closed GC log entry.")
        return self._new_version(
            ctx,
            entity_records=[*self.entity_records, EntitySummary.from_entity(entity)],
        )

    @update_entity_action
    def close(self, ctx: DomainContext) -> "GCLogEntry":
        """Close the GC log entry."""
        return self._new_version(
            ctx,
            opened=False,
        )

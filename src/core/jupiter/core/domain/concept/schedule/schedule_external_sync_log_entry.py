"""An entry in a sync log."""
from jupiter.core.domain.entity_summary import EntitySummary
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
from jupiter.core.framework.value import CompositeValue, value


@value
class ScheduleExternalSyncLogPerStreamResult(CompositeValue):
    """The result of syncing a stream."""

    schedule_stream_ref_id: EntityId
    success: bool
    error_msg: str | None


@entity
class ScheduleExternalSyncLogEntry(LeafEntity):
    """An entry in a sync log."""

    schedule_external_sync_log: ParentLink
    source: EventSource
    filter_schedule_stream_ref_id: list[EntityId] | None
    opened: bool
    per_stream_results: list[ScheduleExternalSyncLogPerStreamResult]
    entity_records: list[EntitySummary]

    @staticmethod
    @create_entity_action
    def new_log_entry(
        ctx: DomainContext,
        schedule_external_sync_log_ref_id: EntityId,
        filter_schedule_stream_ref_id: list[EntityId] | None,
    ) -> "ScheduleExternalSyncLogEntry":
        """Create a new log entry."""
        return ScheduleExternalSyncLogEntry._create(
            ctx,
            name=ScheduleExternalSyncLogEntry.build_name(ctx.action_timestamp),
            schedule_external_sync_log=ParentLink(schedule_external_sync_log_ref_id),
            source=ctx.event_source,
            filter_schedule_stream_ref_id=filter_schedule_stream_ref_id,
            opened=True,
            per_stream_results=[],
            entity_records=[],
        )

    @update_entity_action
    def mark_stream_success(
        self,
        ctx: DomainContext,
        schedule_stream_ref_id: EntityId,
    ) -> "ScheduleExternalSyncLogEntry":
        """Mark a stream as successfully synced."""
        if not self.opened:
            raise Exception("Can't add an entity to a closed GC log entry.")
        return self._new_version(
            ctx,
            per_stream_results=[
                *self.per_stream_results,
                ScheduleExternalSyncLogPerStreamResult(
                    schedule_stream_ref_id=schedule_stream_ref_id,
                    success=True,
                    error_msg=None,
                ),
            ],
        )

    @update_entity_action
    def mark_stream_error(
        self,
        ctx: DomainContext,
        schedule_stream_ref_id: EntityId,
        error_msg: str,
    ) -> "ScheduleExternalSyncLogEntry":
        """Mark a stream as failed to sync."""
        if not self.opened:
            raise Exception("Can't add an entity to a closed GC log entry.")
        return self._new_version(
            ctx,
            per_stream_results=[
                *self.per_stream_results,
                ScheduleExternalSyncLogPerStreamResult(
                    schedule_stream_ref_id=schedule_stream_ref_id,
                    success=False,
                    error_msg=error_msg,
                ),
            ],
        )

    @update_entity_action
    def add_entity(
        self,
        ctx: DomainContext,
        entity: CrownEntity,
    ) -> "ScheduleExternalSyncLogEntry":
        """Add an entity to the GC log entry."""
        if not self.opened:
            raise Exception("Can't add an entity to a closed GC log entry.")
        return self._new_version(
            ctx,
            entity_records=[*self.entity_records, EntitySummary.from_entity(entity)],
        )

    @update_entity_action
    def close(self, ctx: DomainContext) -> "ScheduleExternalSyncLogEntry":
        """Close the log entry."""
        return self._new_version(
            ctx,
            opened=False,
        )

    @staticmethod
    def build_name(created_time: Timestamp) -> EntityName:
        return EntityName(f"Sync log entry {created_time}")

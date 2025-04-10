"""An entry in a sync log."""

import abc

from jupiter.core.domain.core.adate import ADate
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
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.repository import LeafEntityRepository
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
    today: ADate
    start_of_window: ADate
    end_of_window: ADate
    sync_even_if_not_modified: bool
    filter_schedule_stream_ref_id: list[EntityId] | None
    opened: bool
    per_stream_results: list[ScheduleExternalSyncLogPerStreamResult]
    entity_records: list[EntitySummary]
    even_more_entity_records: bool

    @staticmethod
    @create_entity_action
    def new_log_entry(
        ctx: DomainContext,
        schedule_external_sync_log_ref_id: EntityId,
        today: ADate,
        start_of_window: ADate,
        end_of_window: ADate,
        sync_even_if_not_modified: bool,
        filter_schedule_stream_ref_id: list[EntityId] | None,
    ) -> "ScheduleExternalSyncLogEntry":
        """Create a new log entry."""
        if start_of_window > end_of_window:
            raise InputValidationError("Start of window must be before end of window.")
        if today < start_of_window or today > end_of_window:
            raise InputValidationError("Today must be within the window.")
        return ScheduleExternalSyncLogEntry._create(
            ctx,
            name=ScheduleExternalSyncLogEntry.build_name(ctx.action_timestamp),
            schedule_external_sync_log=ParentLink(schedule_external_sync_log_ref_id),
            source=ctx.event_source,
            today=today,
            start_of_window=start_of_window,
            end_of_window=end_of_window,
            sync_even_if_not_modified=sync_even_if_not_modified,
            filter_schedule_stream_ref_id=filter_schedule_stream_ref_id,
            opened=True,
            per_stream_results=[],
            entity_records=[],
            even_more_entity_records=False,
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
        if len(self.entity_records) >= 100:
            return self._new_version(
                ctx,
                even_more_entity_records=True,
            )
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
        """Build the name for this entry."""
        return EntityName(f"Sync log entry {created_time}")


class ScheduleExternalSyncLogEntryRepository(
    LeafEntityRepository[ScheduleExternalSyncLogEntry], abc.ABC
):
    """Repository for ScheduleExternalSyncLogEntry."""

    @abc.abstractmethod
    async def find_last(
        self,
        parent_ref_id: EntityId,
        limit: int,
    ) -> list[ScheduleExternalSyncLogEntry]:
        """Find the last N log entry."""

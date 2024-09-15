"""The service which syncs external calendars with Jupiter."""
from typing import Final, cast

import requests
from icalendar import Calendar
from jupiter.core.domain.concept.schedule.schedule_domain import ScheduleDomain
from jupiter.core.domain.concept.schedule.schedule_external_sync_log import (
    ScheduleExternalSyncLog,
)
from jupiter.core.domain.concept.schedule.schedule_external_sync_log_entry import (
    ScheduleExternalSyncLogEntry,
)
from jupiter.core.domain.concept.schedule.schedule_source import ScheduleSource
from jupiter.core.domain.concept.schedule.schedule_stream import ScheduleStream
from jupiter.core.domain.concept.schedule.schedule_stream_color import (
    ScheduleStreamColor,
)
from jupiter.core.domain.concept.schedule.schedule_stream_name import ScheduleStreamName
from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.domain.core.url import URL
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import NoFilter
from jupiter.core.framework.realm import RealmCodecRegistry, RealmDecodingError
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


class ScheduleExternalSyncService:
    """The service which syncs external calendars with Jupiter."""

    _time_provider: Final[TimeProvider]
    _realm_codec_registry: Final[RealmCodecRegistry]
    _domain_storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        time_provider: TimeProvider,
        realm_codec_registry: RealmCodecRegistry,
        domain_storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._realm_codec_registry = realm_codec_registry
        self._domain_storage_engine = domain_storage_engine

    async def do_it(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        workspace: Workspace,
        filter_schedule_stream_ref_id: list[EntityId] | None,
    ) -> None:
        """Execute the sync action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            schedule_domain = await uow.get_for(ScheduleDomain).load_by_parent(
                workspace.ref_id
            )
            # This loading is a bit of a hack. No load_by_parent for branches yet.
            sync_logs = await uow.get_for(ScheduleExternalSyncLog).find_all(
                parent_ref_id=schedule_domain.ref_id,
                allow_archived=False,
            )
            if len(sync_logs) != 1:
                raise Exception("Expected exactly one sync log for the schedule domain")
            sync_log = sync_logs[0]
            sync_log_entry = ScheduleExternalSyncLogEntry.new_log_entry(
                ctx,
                schedule_external_sync_log_ref_id=sync_log.ref_id,
                filter_schedule_stream_ref_id=filter_schedule_stream_ref_id,
            )
            sync_log_entry = await uow.get_for(ScheduleExternalSyncLogEntry).create(
                sync_log_entry
            )

            schedule_streams = await uow.get_for(ScheduleStream).find_all_generic(
                parent_ref_id=schedule_domain.ref_id,
                allow_archived=False,
                source=ScheduleSource.EXTERNAL_ICAL,
                ref_id=filter_schedule_stream_ref_id or NoFilter(),
            )

        for schedule_stream in schedule_streams:
            sync_log_entry = await self._process_schedule_stream(
                ctx, progress_reporter, schedule_stream, sync_log_entry
            )

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            sync_log_entry = sync_log_entry.close(ctx)
            sync_log_entry = await uow.get_for(ScheduleExternalSyncLogEntry).save(
                sync_log_entry
            )

    async def _process_schedule_stream(
        self,
        ctx: DomainContext,
        progress_reporter: ProgressReporter,
        schedule_stream: ScheduleStream,
        sync_log_entry: ScheduleExternalSyncLogEntry,
    ) -> ScheduleExternalSyncLogEntry:
        """Process a schedule stream."""
        # Step 1: Fetch the iCal
        try:
            calendar_ical_response = requests.get(
                cast(URL, schedule_stream.source_ical_url).the_url
            )
            if calendar_ical_response.status_code != 200:
                # Early exit mark some error in sync log entry
                return sync_log_entry.mark_stream_error(
                    ctx,
                    schedule_stream_ref_id=schedule_stream.ref_id,
                    error_msg=f"Failed to fetch iCal from {schedule_stream.source_ical_url} (error {calendar_ical_response.status_code})",
                )
            calendar_ical = calendar_ical_response.text
        except requests.RequestException as err:
            # Early exit in sync log entry
            return sync_log_entry.mark_stream_error(
                ctx,
                schedule_stream_ref_id=schedule_stream.ref_id,
                error_msg=f"Failed to fetch iCal from {schedule_stream.source_ical_url} ({err})",
            )

        try:
            calendar = Calendar.from_ical(calendar_ical)
        except ValueError as err:
            # Early exit in sync log entry
            return sync_log_entry.mark_stream_error(
                ctx,
                schedule_stream_ref_id=schedule_stream.ref_id,
                error_msg=f"Failed to parse iCal from {schedule_stream.source_ical_url} ({err})",
            )

        # Step 2: Update the schedule stream
        name = self._realm_codec_registry.db_decode(
            ScheduleStreamName, calendar.get("X-WR-CALNAME")
        )
        try:
            color = self._realm_codec_registry.db_decode(
                ScheduleStreamColor, calendar.get("COLOR")
            )
        except RealmDecodingError:
            color = schedule_stream.color

        schedule_stream = schedule_stream.update(
            ctx,
            name=UpdateAction.change_to(name),
            color=UpdateAction.change_to(color),
        )
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            await uow.get_for(ScheduleStream).save(schedule_stream)
            await progress_reporter.mark_updated(schedule_stream)

        sync_log_entry = sync_log_entry.add_entity(ctx, schedule_stream)

        # Step 3: Process the events

        # Step 4: Archive old events not present in the stream anymore

        return sync_log_entry.mark_stream_success(
            ctx, schedule_stream_ref_id=schedule_stream.ref_id
        )

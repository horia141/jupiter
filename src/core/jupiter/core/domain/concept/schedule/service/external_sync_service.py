"""The service which syncs external calendars with jupiter."""
from typing import Final, cast

import recurring_ical_events
import requests
from icalendar import Calendar
from icalendar.cal import Component
from jupiter.core.domain.concept.schedule.schedule_domain import ScheduleDomain
from jupiter.core.domain.concept.schedule.schedule_event_full_days import (
    ScheduleEventFullDays,
)
from jupiter.core.domain.concept.schedule.schedule_event_in_day import (
    ScheduleEventInDay,
)
from jupiter.core.domain.concept.schedule.schedule_event_name import ScheduleEventName
from jupiter.core.domain.concept.schedule.schedule_external_sync_log import (
    ScheduleExternalSyncLog,
)
from jupiter.core.domain.concept.schedule.schedule_external_sync_log_entry import (
    ScheduleExternalSyncLogEntry,
)
from jupiter.core.domain.concept.schedule.schedule_external_uid import (
    ScheduleExternalUid,
)
from jupiter.core.domain.concept.schedule.schedule_source import ScheduleSource
from jupiter.core.domain.concept.schedule.schedule_stream import ScheduleStream
from jupiter.core.domain.concept.schedule.schedule_stream_name import ScheduleStreamName
from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_content_block import (
    CorrelationId,
    OneOfNoteContentBlock,
    ParagraphBlock,
)
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.time_events.time_event_domain import TimeEventDomain
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
)
from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    MAX_DURATION_MINS,
    TimeEventInDayBlock,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.domain.core.time_in_day import TimeInDay
from jupiter.core.domain.core.url import URL
from jupiter.core.domain.infra.generic_crown_archiver import generic_crown_archiver
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import NoFilter
from jupiter.core.framework.realm import RealmCodecRegistry
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.utils.time_provider import TimeProvider
from pendulum import Date


class ScheduleExternalSyncService:
    """The service which syncs external calendars with jupiter."""

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
        today: ADate,
        sync_even_if_not_modified: bool,
        filter_schedule_stream_ref_id: list[EntityId] | None,
    ) -> None:
        """Execute the sync action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            schedule_domain = await uow.get_for(ScheduleDomain).load_by_parent(
                workspace.ref_id
            )
            time_event_domain = await uow.get_for(TimeEventDomain).load_by_parent(
                workspace.ref_id
            )
            note_collection = await uow.get_for(NoteCollection).load_by_parent(
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

            start_of_window, end_of_window = self._build_processing_window(today)
            sync_log_entry = ScheduleExternalSyncLogEntry.new_log_entry(
                ctx,
                schedule_external_sync_log_ref_id=sync_log.ref_id,
                today=today,
                start_of_window=start_of_window,
                end_of_window=end_of_window,
                sync_even_if_not_modified=sync_even_if_not_modified,
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

            all_time_event_full_days_blocks = await uow.get_for(
                TimeEventFullDaysBlock
            ).find_all_generic(
                parent_ref_id=time_event_domain.ref_id,
                allow_archived=False,
                namespace=TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK,
            )
            all_time_event_full_days_blocks_by_source_entity_ref_id = {
                block.source_entity_ref_id: block
                for block in all_time_event_full_days_blocks
            }

            all_time_event_in_day_blocks = await uow.get_for(
                TimeEventInDayBlock
            ).find_all_generic(
                parent_ref_id=time_event_domain.ref_id,
                allow_archived=False,
                namespace=TimeEventNamespace.SCHEDULE_EVENT_IN_DAY,
            )
            all_time_event_in_day_blocks_by_source_entity_ref_id = {
                block.source_entity_ref_id: block
                for block in all_time_event_in_day_blocks
            }

            all_notes_for_dull_days = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                allow_archived=False,
                domain=NoteDomain.SCHEDULE_EVENT_FULL_DAYS,
            )
            all_notes_for_dull_days_by_source_entity_ref_id = {
                note.source_entity_ref_id: note for note in all_notes_for_dull_days
            }

            all_notes_for_in_day = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                allow_archived=False,
                domain=NoteDomain.SCHEDULE_EVENT_IN_DAY,
            )
            all_notes_for_in_day_by_source_entity_ref_id = {
                note.source_entity_ref_id: note for note in all_notes_for_in_day
            }

        for schedule_stream in schedule_streams:
            sync_log_entry = await self._process_schedule_stream(
                ctx,
                today,
                start_of_window,
                end_of_window,
                sync_even_if_not_modified,
                progress_reporter,
                schedule_domain,
                time_event_domain,
                note_collection,
                all_time_event_full_days_blocks_by_source_entity_ref_id,
                all_time_event_in_day_blocks_by_source_entity_ref_id,
                all_notes_for_dull_days_by_source_entity_ref_id,
                all_notes_for_in_day_by_source_entity_ref_id,
                schedule_stream,
                sync_log_entry,
            )

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            sync_log_entry = sync_log_entry.close(ctx)
            sync_log_entry = await uow.get_for(ScheduleExternalSyncLogEntry).save(
                sync_log_entry
            )

    async def _process_schedule_stream(
        self,
        ctx: DomainContext,
        today: ADate,
        start_of_window: ADate,
        end_of_window: ADate,
        sync_even_if_not_modified: bool,
        progress_reporter: ProgressReporter,
        schedule_domain: ScheduleDomain,
        time_event_domain: TimeEventDomain,
        note_collection: NoteCollection,
        all_time_event_full_days_blocks_by_source_entity_ref_id: dict[
            EntityId, TimeEventFullDaysBlock
        ],
        all_time_event_in_day_blocks_by_source_entity_ref_id: dict[
            EntityId, TimeEventInDayBlock
        ],
        all_notes_for_dull_days_by_source_entity_ref_id: dict[EntityId, Note],
        all_notes_for_in_day_by_source_entity_ref_id: dict[EntityId, Note],
        schedule_stream: ScheduleStream,
        sync_log_entry: ScheduleExternalSyncLogEntry,
    ) -> ScheduleExternalSyncLogEntry:
        """Process a schedule stream."""
        # Step 1: Fetch the iCal
        try:
            async with progress_reporter.section("Processing stream"):
                calendar = self._retrieve_calendar_ical(schedule_stream)

                # Step 2: Update the schedule stream
                name = self._realm_codec_registry.db_decode(
                    ScheduleStreamName, calendar.get("X-WR-CALNAME")
                )

                schedule_stream = schedule_stream.update(
                    ctx,
                    name=UpdateAction.change_to(name),
                    color=UpdateAction.do_nothing(),
                )
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    await uow.get_for(ScheduleStream).save(schedule_stream)
                    await progress_reporter.mark_updated(schedule_stream)

                sync_log_entry = sync_log_entry.add_entity(ctx, schedule_stream)

            newly_created_schedule_full_days: set[EntityId] = set()
            newly_created_schedule_in_day: set[EntityId] = set()

            # Step 3: Process the events
            async with progress_reporter.section("Adding and updating events"):
                async with self._domain_storage_engine.get_unit_of_work() as uow:
                    all_full_days_events = await uow.get_for(
                        ScheduleEventFullDays
                    ).find_all_generic(
                        parent_ref_id=schedule_domain.ref_id,
                        allow_archived=False,
                        schedule_stream_ref_id=schedule_stream.ref_id,
                    )
                    all_in_day_events = await uow.get_for(
                        ScheduleEventInDay
                    ).find_all_generic(
                        parent_ref_id=schedule_domain.ref_id,
                        allow_archived=False,
                        schedule_stream_ref_id=schedule_stream.ref_id,
                    )

                all_full_days_events_by_external_uid = {
                    event.external_uid: event for event in all_full_days_events
                }
                all_in_day_events_by_external_uid = {
                    event.external_uid: event for event in all_in_day_events
                }

                processed_events_external_uids = set()

                all_events = recurring_ical_events.of(calendar).between(
                    start_of_window.the_date, end_of_window.the_date
                )

                for event in all_events:
                    if (
                        "SUMMARY" not in event
                        or "UID" not in event
                        or "DTSTART" not in event
                        or "DTEND" not in event
                    ):
                        # Skipping events that are malformed
                        continue

                    if (
                        "value" in event["DTSTART"].params
                        and event["DTSTART"].params["value"] == "DATE"
                        and "value" in event["DTEND"].params
                        and event["DTEND"].params["value"] == "DATE"
                    ):
                        # Full day event
                        event_name = self._realm_codec_registry.db_decode(
                            ScheduleEventName, event["SUMMARY"]
                        )
                        uid_base = self._realm_codec_registry.db_decode(
                            ScheduleExternalUid, event["UID"].to_ical().decode()
                        )
                        start_date = self._realm_codec_registry.db_decode(
                            ADate, event["DTSTART"].dt
                        )
                        uid = ScheduleExternalUid.from_string(
                            f"{uid_base.the_uid}:{start_date}"
                        )
                        end_date = self._realm_codec_registry.db_decode(
                            ADate, event["DTEND"].dt
                        )
                        if "RECURRENCE-ID" in event:
                            recurrence_id = self._realm_codec_registry.db_decode(
                                Timestamp, event["RECURRENCE-ID"].dt
                            )
                            uid = ScheduleExternalUid.from_string(
                                f"{uid.the_uid}:{recurrence_id}"
                            )
                        last_modified = None
                        if "LAST-MODIFIED" in event:
                            last_modified = self._realm_codec_registry.db_decode(
                                Timestamp, event["LAST-MODIFIED"].dt
                            )
                        description = (
                            str(event["DESCRIPTION"])
                            if "DESCRIPTION" in event
                            else None
                        )

                        if uid not in all_full_days_events_by_external_uid:
                            async with self._domain_storage_engine.get_unit_of_work() as uow:
                                schedule_event_full_days = ScheduleEventFullDays.new_schedule_full_days_block_from_external_ical(
                                    ctx,
                                    schedule_domain_ref_id=schedule_domain.ref_id,
                                    schedule_stream_ref_id=schedule_stream.ref_id,
                                    name=event_name,
                                    external_uid=uid,
                                )

                                schedule_event_full_days = await uow.get_for(
                                    ScheduleEventFullDays
                                ).create(schedule_event_full_days)
                                await progress_reporter.mark_created(
                                    schedule_event_full_days
                                )
                                newly_created_schedule_full_days.add(
                                    schedule_event_full_days.ref_id
                                )

                                time_event_full_days_block = TimeEventFullDaysBlock.new_time_event_for_schedule_event(
                                    ctx,
                                    time_event_domain_ref_id=time_event_domain.ref_id,
                                    schedule_event_ref_id=schedule_event_full_days.ref_id,
                                    start_date=start_date,
                                    duration_days=end_date.days_since(start_date),
                                )
                                time_event_full_days_block = await uow.get_for(
                                    TimeEventFullDaysBlock
                                ).create(time_event_full_days_block)

                                if description is not None:
                                    note_content: list[OneOfNoteContentBlock] = [
                                        ParagraphBlock(
                                            kind="paragraph",
                                            correlation_id=CorrelationId("0"),
                                            text=description,
                                        )
                                    ]
                                    note: Note | None = Note.new_note(
                                        ctx,
                                        note_collection_ref_id=note_collection.ref_id,
                                        domain=NoteDomain.SCHEDULE_EVENT_FULL_DAYS,
                                        source_entity_ref_id=schedule_event_full_days.ref_id,
                                        content=note_content,
                                    )
                                    note = await uow.get_for(Note).create(
                                        cast(Note, note)
                                    )
                                    all_notes_for_dull_days_by_source_entity_ref_id[
                                        schedule_event_full_days.ref_id
                                    ] = note

                                all_full_days_events.append(schedule_event_full_days)
                                all_full_days_events_by_external_uid[
                                    uid
                                ] = schedule_event_full_days
                                all_time_event_full_days_blocks_by_source_entity_ref_id[
                                    schedule_event_full_days.ref_id
                                ] = time_event_full_days_block
                                sync_log_entry = sync_log_entry.add_entity(
                                    ctx, schedule_event_full_days
                                )
                        elif (
                            sync_even_if_not_modified
                            or (last_modified is None)
                            or (
                                last_modified
                                > all_full_days_events_by_external_uid[
                                    uid
                                ].last_modified_time
                            )
                        ):
                            async with self._domain_storage_engine.get_unit_of_work() as uow:
                                schedule_event_full_days = (
                                    all_full_days_events_by_external_uid[uid]
                                )
                                schedule_event_full_days = (
                                    schedule_event_full_days.update(
                                        ctx,
                                        name=UpdateAction.change_to(event_name),
                                    )
                                )
                                await uow.get_for(ScheduleEventFullDays).save(
                                    schedule_event_full_days
                                )
                                await progress_reporter.mark_updated(
                                    schedule_event_full_days
                                )

                                time_event_full_days_block = all_time_event_full_days_blocks_by_source_entity_ref_id[
                                    schedule_event_full_days.ref_id
                                ]
                                time_event_full_days_block = time_event_full_days_block.update_for_schedule_event(
                                    ctx,
                                    start_date=UpdateAction.change_to(start_date),
                                    duration_days=UpdateAction.change_to(
                                        end_date.days_since(start_date)
                                    ),
                                )
                                await uow.get_for(TimeEventFullDaysBlock).save(
                                    time_event_full_days_block
                                )

                                if description is not None:
                                    note = all_notes_for_dull_days_by_source_entity_ref_id.get(
                                        schedule_event_full_days.ref_id, None
                                    )
                                    if note is None:
                                        note_content = [
                                            ParagraphBlock(
                                                kind="paragraph",
                                                correlation_id=CorrelationId("0"),
                                                text=description,
                                            )
                                        ]
                                        note = Note.new_note(
                                            ctx,
                                            note_collection_ref_id=note_collection.ref_id,
                                            domain=NoteDomain.SCHEDULE_EVENT_FULL_DAYS,
                                            source_entity_ref_id=schedule_event_full_days.ref_id,
                                            content=note_content,
                                        )
                                        note = await uow.get_for(Note).create(note)
                                        all_notes_for_dull_days_by_source_entity_ref_id[
                                            schedule_event_full_days.ref_id
                                        ] = note
                                    else:
                                        note_content = [
                                            ParagraphBlock(
                                                kind="paragraph",
                                                correlation_id=CorrelationId("0"),
                                                text=description,
                                            )
                                        ]
                                        note = note.update(
                                            ctx,
                                            content=UpdateAction.change_to(
                                                note_content
                                            ),
                                        )
                                        await uow.get_for(Note).save(note)
                                else:
                                    note = all_notes_for_dull_days_by_source_entity_ref_id.get(
                                        schedule_event_full_days.ref_id, None
                                    )
                                    if note is not None:
                                        # We don't archive right now, but just blank the content. We don't have a
                                        # good story on archival and de-archival right now.
                                        note_content = [
                                            ParagraphBlock(
                                                kind="paragraph",
                                                correlation_id=CorrelationId("0"),
                                                text="",
                                            )
                                        ]
                                        note = note.update(
                                            ctx,
                                            content=UpdateAction.change_to(
                                                note_content
                                            ),
                                        )
                                        await uow.get_for(Note).save(note)

                                if (
                                    schedule_event_full_days.ref_id
                                    not in newly_created_schedule_full_days
                                ):
                                    sync_log_entry = sync_log_entry.add_entity(
                                        ctx, schedule_event_full_days
                                    )

                        processed_events_external_uids.add(uid)
                    elif (
                        "value" not in event["DTSTART"].params
                        and "value" not in event["DTEND"].params
                    ):
                        # In-day event
                        event_name = self._realm_codec_registry.db_decode(
                            ScheduleEventName, event["SUMMARY"]
                        )
                        uid_base = self._realm_codec_registry.db_decode(
                            ScheduleExternalUid, event["UID"].to_ical().decode()
                        )
                        # icalendar makes everything UTC so we don't need to.
                        start_time = self._realm_codec_registry.db_decode(
                            Timestamp, event["DTSTART"].dt
                        )
                        uid = ScheduleExternalUid.from_string(
                            f"{uid_base.the_uid}:{start_time}"
                        )
                        end_time = self._realm_codec_registry.db_decode(
                            Timestamp, event["DTEND"].dt
                        )
                        if "RECURRENCE-ID" in event:
                            recurrence_id = self._realm_codec_registry.db_decode(
                                Timestamp, event["RECURRENCE-ID"].dt
                            )
                            uid = ScheduleExternalUid.from_string(
                                f"{uid.the_uid}:{recurrence_id}"
                            )
                        last_modified = None
                        if "LAST-MODIFIED" in event:
                            last_modified = self._realm_codec_registry.db_decode(
                                Timestamp, event["LAST-MODIFIED"].dt
                            )
                        description = (
                            str(event["DESCRIPTION"])
                            if "DESCRIPTION" in event
                            else None
                        )

                        total_duration = min(
                            MAX_DURATION_MINS, end_time.mins_since(start_time)
                        )

                        if uid not in all_in_day_events_by_external_uid:
                            async with self._domain_storage_engine.get_unit_of_work() as uow:
                                schedule_event_in_day = ScheduleEventInDay.new_schedule_event_in_day_from_external_ical(
                                    ctx,
                                    schedule_domain_ref_id=schedule_domain.ref_id,
                                    schedule_stream_ref_id=schedule_stream.ref_id,
                                    name=event_name,
                                    external_uid=uid,
                                )
                                schedule_event_in_day = await uow.get_for(
                                    ScheduleEventInDay
                                ).create(schedule_event_in_day)
                                await progress_reporter.mark_created(
                                    schedule_event_in_day
                                )
                                newly_created_schedule_in_day.add(
                                    schedule_event_in_day.ref_id
                                )

                                time_event_in_day_block = TimeEventInDayBlock.new_time_event_for_schedule_event(
                                    ctx,
                                    time_event_domain_ref_id=time_event_domain.ref_id,
                                    schedule_event_ref_id=schedule_event_in_day.ref_id,
                                    start_date=ADate.from_date(start_time.as_date()),
                                    start_time_in_day=TimeInDay.from_parts(
                                        start_time.value.hour, start_time.value.minute
                                    ),
                                    duration_mins=total_duration,
                                )
                                time_event_in_day_block = await uow.get_for(
                                    TimeEventInDayBlock
                                ).create(time_event_in_day_block)

                                if description is not None:
                                    note_content = [
                                        ParagraphBlock(
                                            kind="paragraph",
                                            correlation_id=CorrelationId("0"),
                                            text=description,
                                        )
                                    ]
                                    note = Note.new_note(
                                        ctx,
                                        note_collection_ref_id=note_collection.ref_id,
                                        domain=NoteDomain.SCHEDULE_EVENT_IN_DAY,
                                        source_entity_ref_id=schedule_event_in_day.ref_id,
                                        content=note_content,
                                    )
                                    note = await uow.get_for(Note).create(note)

                                all_in_day_events.append(schedule_event_in_day)
                                all_in_day_events_by_external_uid[
                                    uid
                                ] = schedule_event_in_day
                                all_time_event_in_day_blocks_by_source_entity_ref_id[
                                    schedule_event_in_day.ref_id
                                ] = time_event_in_day_block
                                sync_log_entry = sync_log_entry.add_entity(
                                    ctx, schedule_event_in_day
                                )
                        elif (
                            sync_even_if_not_modified
                            or (last_modified is None)
                            or (
                                last_modified
                                > all_in_day_events_by_external_uid[
                                    uid
                                ].last_modified_time
                            )
                        ):
                            async with self._domain_storage_engine.get_unit_of_work() as uow:
                                schedule_event_in_day = (
                                    all_in_day_events_by_external_uid[uid]
                                )
                                schedule_event_in_day = schedule_event_in_day.update(
                                    ctx,
                                    name=UpdateAction.change_to(event_name),
                                )
                                await uow.get_for(ScheduleEventInDay).save(
                                    schedule_event_in_day
                                )
                                await progress_reporter.mark_updated(
                                    schedule_event_in_day
                                )

                                time_event_in_day_block = all_time_event_in_day_blocks_by_source_entity_ref_id[
                                    schedule_event_in_day.ref_id
                                ]
                                time_event_in_day_block = (
                                    time_event_in_day_block.update(
                                        ctx,
                                        start_date=UpdateAction.change_to(
                                            ADate.from_date(start_time.as_date())
                                        ),
                                        start_time_in_day=UpdateAction.change_to(
                                            TimeInDay.from_parts(
                                                start_time.value.hour,
                                                start_time.value.minute,
                                            )
                                        ),
                                        duration_mins=UpdateAction.change_to(
                                            total_duration
                                        ),
                                    )
                                )
                                await uow.get_for(TimeEventInDayBlock).save(
                                    time_event_in_day_block
                                )

                                if description is not None:
                                    note = all_notes_for_in_day_by_source_entity_ref_id.get(
                                        schedule_event_in_day.ref_id, None
                                    )
                                    if note is None:
                                        note_content = [
                                            ParagraphBlock(
                                                kind="paragraph",
                                                correlation_id=CorrelationId("0"),
                                                text=description,
                                            )
                                        ]
                                        note = Note.new_note(
                                            ctx,
                                            note_collection_ref_id=note_collection.ref_id,
                                            domain=NoteDomain.SCHEDULE_EVENT_IN_DAY,
                                            source_entity_ref_id=schedule_event_in_day.ref_id,
                                            content=note_content,
                                        )
                                        note = await uow.get_for(Note).create(note)
                                        all_notes_for_in_day_by_source_entity_ref_id[
                                            schedule_event_in_day.ref_id
                                        ] = note
                                    else:
                                        note_content = [
                                            ParagraphBlock(
                                                kind="paragraph",
                                                correlation_id=CorrelationId("0"),
                                                text=description,
                                            )
                                        ]
                                        note = note.update(
                                            ctx,
                                            content=UpdateAction.change_to(
                                                note_content
                                            ),
                                        )
                                        await uow.get_for(Note).save(note)
                                else:
                                    note = all_notes_for_in_day_by_source_entity_ref_id.get(
                                        schedule_event_in_day.ref_id, None
                                    )
                                    if note is not None:
                                        # We don't archive right now, but just blank the content. We don't have a
                                        # good story on archival and de-archival right now.
                                        note_content = [
                                            ParagraphBlock(
                                                kind="paragraph",
                                                correlation_id=CorrelationId("0"),
                                                text="",
                                            )
                                        ]
                                        note = note.update(
                                            ctx,
                                            content=UpdateAction.change_to(
                                                note_content
                                            ),
                                        )
                                        await uow.get_for(Note).save(note)

                                if (
                                    schedule_event_in_day.ref_id
                                    not in newly_created_schedule_in_day
                                ):
                                    sync_log_entry = sync_log_entry.add_entity(
                                        ctx, schedule_event_in_day
                                    )

                        processed_events_external_uids.add(uid)
                    else:
                        return sync_log_entry.mark_stream_error(
                            ctx,
                            schedule_stream_ref_id=schedule_stream.ref_id,
                            error_msg=f"Unexpected event type {event}",
                        )

            # Step 4: Archive old events not present in the stream anymore
            async with progress_reporter.section("Archiving old events"):
                for schedule_event_full_days in all_full_days_events:
                    if (
                        schedule_event_full_days.external_uid
                        in processed_events_external_uids
                    ):
                        continue

                    time_event_full_days_block = (
                        all_time_event_full_days_blocks_by_source_entity_ref_id[
                            schedule_event_full_days.ref_id
                        ]
                    )
                    if time_event_full_days_block.start_date < start_of_window:
                        continue

                    async with self._domain_storage_engine.get_unit_of_work() as uow:
                        await generic_crown_archiver(
                            ctx,
                            uow,
                            progress_reporter,
                            ScheduleEventFullDays,
                            schedule_event_full_days.ref_id,
                        )
                        sync_log_entry = sync_log_entry.add_entity(
                            ctx, schedule_event_full_days
                        )

                for schedule_event_in_day in all_in_day_events:
                    if (
                        schedule_event_in_day.external_uid
                        in processed_events_external_uids
                    ):
                        continue

                    time_event_in_day_block = (
                        all_time_event_in_day_blocks_by_source_entity_ref_id[
                            schedule_event_in_day.ref_id
                        ]
                    )
                    if time_event_in_day_block.start_date < start_of_window:
                        continue

                    async with self._domain_storage_engine.get_unit_of_work() as uow:
                        await generic_crown_archiver(
                            ctx,
                            uow,
                            progress_reporter,
                            ScheduleEventInDay,
                            schedule_event_in_day.ref_id,
                        )
                        sync_log_entry = sync_log_entry.add_entity(
                            ctx, schedule_event_in_day
                        )

            # Step 5: done!

            return sync_log_entry.mark_stream_success(
                ctx, schedule_stream_ref_id=schedule_stream.ref_id
            )
        except ValueError as err:
            return sync_log_entry.mark_stream_error(
                ctx,
                schedule_stream_ref_id=schedule_stream.ref_id,
                error_msg=f"{err}",
            )

    def _retrieve_calendar_ical(self, schedule_stream: ScheduleStream) -> Component:
        """Retrieve the iCal for a schedule stream."""
        try:
            calendar_ical_response = requests.get(
                cast(URL, schedule_stream.source_ical_url).the_url
            )
            if calendar_ical_response.status_code != 200:
                # Early exit mark some error in sync log entry
                raise ValueError(
                    f"Failed to fetch iCal from {schedule_stream.source_ical_url} (error {calendar_ical_response.status_code})"
                )
            calendar_ical = calendar_ical_response.text
        except requests.RequestException as err:
            # Early exit in sync log entry
            raise ValueError(
                f"Failed to fetch iCal from {schedule_stream.source_ical_url} ({err})"
            ) from err

        try:
            calendar = Calendar.from_ical(calendar_ical)
        except ValueError as err:
            # Early exit in sync log entry
            raise ValueError(
                f"Failed to parse iCal from {schedule_stream.source_ical_url} ({err})"
            ) from err

        return calendar

    def _build_processing_window(self, today: ADate) -> tuple[ADate, ADate]:
        """Build the processing window."""
        today_date = today.the_date
        start_of_window = cast(Date, today_date.start_of("year").add(years=-1))  # type: ignore
        end_of_window = cast(Date, today_date.add(days=30).end_of("year"))  # type: ignore
        return (ADate.from_date(start_of_window), ADate.from_date(end_of_window))

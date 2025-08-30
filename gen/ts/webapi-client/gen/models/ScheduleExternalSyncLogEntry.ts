/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { EntitySummary } from './EntitySummary';
import type { EventSource } from './EventSource';
import type { ScheduleExternalSyncLogPerStreamResult } from './ScheduleExternalSyncLogPerStreamResult';
import type { Timestamp } from './Timestamp';
/**
 * An entry in a sync log.
 */
export type ScheduleExternalSyncLogEntry = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    schedule_external_sync_log_ref_id: string;
    source: EventSource;
    today: ADate;
    start_of_window: ADate;
    end_of_window: ADate;
    sync_even_if_not_modified: boolean;
    filter_schedule_stream_ref_id?: (Array<EntityId> | null);
    opened: boolean;
    per_stream_results: Array<ScheduleExternalSyncLogPerStreamResult>;
    entity_records: Array<EntitySummary>;
    even_more_entity_records: boolean;
};


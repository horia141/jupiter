/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { EntitySummary } from './EntitySummary';
import type { EventSource } from './EventSource';
import type { SyncTarget } from './SyncTarget';
import type { Timestamp } from './Timestamp';
/**
 * A particular entry in the stats log.
 */
export type StatsLogEntry = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    stats_log_ref_id: string;
    source: EventSource;
    stats_targets: Array<SyncTarget>;
    today: ADate;
    filter_big_plan_ref_ids?: (Array<EntityId> | null);
    filter_journal_ref_ids?: (Array<EntityId> | null);
    filter_habit_ref_ids?: (Array<EntityId> | null);
    opened: boolean;
    entity_records: Array<EntitySummary>;
};


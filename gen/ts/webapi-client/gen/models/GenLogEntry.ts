/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { EntitySummary } from './EntitySummary';
import type { EventSource } from './EventSource';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { SyncTarget } from './SyncTarget';
import type { Timestamp } from './Timestamp';
/**
 * A particular entry in the task generation log.
 */
export type GenLogEntry = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    gen_log_ref_id: string;
    source: EventSource;
    gen_even_if_not_modified: boolean;
    today: ADate;
    gen_targets: Array<SyncTarget>;
    period?: (Array<RecurringTaskPeriod> | null);
    filter_project_ref_ids?: (Array<EntityId> | null);
    filter_habit_ref_ids?: (Array<EntityId> | null);
    filter_chore_ref_ids?: (Array<EntityId> | null);
    filter_metric_ref_ids?: (Array<EntityId> | null);
    filter_person_ref_ids?: (Array<EntityId> | null);
    filter_slack_task_ref_ids?: (Array<EntityId> | null);
    filter_email_task_ref_ids?: (Array<EntityId> | null);
    opened: boolean;
    entity_created_records: Array<EntitySummary>;
    entity_updated_records: Array<EntitySummary>;
    entity_removed_records: Array<EntitySummary>;
};


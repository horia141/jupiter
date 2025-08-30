/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { JournalSource } from './JournalSource';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { Timestamp } from './Timestamp';
/**
 * A journal for a particular range.
 */
export type Journal = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    journal_collection_ref_id: string;
    source: JournalSource;
    right_now: ADate;
    period: RecurringTaskPeriod;
    timeline: string;
};


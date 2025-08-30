/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { Timestamp } from './Timestamp';
/**
 * An entry in the working_mem.txt system.
 */
export type WorkingMem = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    working_mem_collection_ref_id: string;
    right_now: ADate;
    period: RecurringTaskPeriod;
    timeline: string;
};


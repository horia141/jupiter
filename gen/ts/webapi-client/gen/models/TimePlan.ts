/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { TimePlanSource } from './TimePlanSource';
import type { Timestamp } from './Timestamp';
/**
 * A plan for a particular period of time.
 */
export type TimePlan = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    time_plan_domain_ref_id: string;
    source: TimePlanSource;
    right_now: ADate;
    period: RecurringTaskPeriod;
    timeline: string;
    start_date: ADate;
    end_date: ADate;
};


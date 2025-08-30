/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { RecurringTaskGenParams } from './RecurringTaskGenParams';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { TimePlanGenerationApproach } from './TimePlanGenerationApproach';
import type { Timestamp } from './Timestamp';
/**
 * A time plan trunk domain object.
 */
export type TimePlanDomain = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    workspace_ref_id: string;
    periods: Array<RecurringTaskPeriod>;
    generation_approach: TimePlanGenerationApproach;
    generation_in_advance_days: Record<string, number>;
    planning_task_project_ref_id: EntityId;
    planning_task_gen_params?: (RecurringTaskGenParams | null);
};


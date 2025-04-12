/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { BigPlanName } from './BigPlanName';
import type { BigPlanStatus } from './BigPlanStatus';
import type { EntityId } from './EntityId';
import type { Timestamp } from './Timestamp';
/**
 * A big plan.
 */
export type BigPlan = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: BigPlanName;
    big_plan_collection_ref_id: string;
    project_ref_id: EntityId;
    status: BigPlanStatus;
    actionable_date?: (ADate | null);
    due_date?: (ADate | null);
    working_time?: (Timestamp | null);
    completed_time?: (Timestamp | null);
};


/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Timestamp } from './Timestamp';
/**
 * Stats about a big plan.
 */
export type BigPlanStats = {
    created_time: Timestamp;
    last_modified_time: Timestamp;
    big_plan_ref_id: string;
    all_inbox_tasks_cnt: number;
    completed_inbox_tasks_cnt: number;
};


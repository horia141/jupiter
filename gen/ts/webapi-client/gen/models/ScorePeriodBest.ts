/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { Timestamp } from './Timestamp';
/**
 * The best score for a period of time and a particular subdivision of it.
 */
export type ScorePeriodBest = {
    created_time: Timestamp;
    last_modified_time: Timestamp;
    score_log_ref_id: string;
    period?: (RecurringTaskPeriod | null);
    timeline: string;
    sub_period: RecurringTaskPeriod;
    total_score: number;
    inbox_task_cnt: number;
    big_plan_cnt: number;
};


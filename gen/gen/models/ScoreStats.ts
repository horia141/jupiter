/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { Timestamp } from './Timestamp';

/**
 * Statistics about scores for a particular time interval.
 */
export type ScoreStats = {
    created_time: Timestamp;
    last_modified_time: Timestamp;
    score_log: string;
    period?: RecurringTaskPeriod;
    timeline: string;
    total_score: number;
    inbox_task_cnt: number;
    big_plan_cnt: number;
};


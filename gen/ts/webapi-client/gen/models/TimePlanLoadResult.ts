/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Note } from './Note';
import type { TimePlan } from './TimePlan';
import type { TimePlanActivity } from './TimePlanActivity';

/**
 * Result.
 */
export type TimePlanLoadResult = {
    time_plan: TimePlan;
    note: Note;
    activities: Array<TimePlanActivity>;
    sub_period_time_plans: Array<TimePlan>;
};


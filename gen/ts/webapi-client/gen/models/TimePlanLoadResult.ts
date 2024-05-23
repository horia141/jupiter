/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BigPlan } from './BigPlan';
import type { InboxTask } from './InboxTask';
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
    target_inbox_tasks: Array<InboxTask>;
    target_big_plans?: (Array<BigPlan> | null);
    completed_nontarget_inbox_tasks: Array<InboxTask>;
    completed_nottarget_big_plans?: (Array<BigPlan> | null);
    sub_period_time_plans: Array<TimePlan>;
    higher_time_plan?: (TimePlan | null);
    previous_time_plan?: (TimePlan | null);
};


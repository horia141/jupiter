/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { InboxTask } from './InboxTask';
import type { TimePlanActivity } from './TimePlanActivity';

/**
 * InboxTaskCreate result.
 */
export type InboxTaskCreateResult = {
    new_inbox_task: InboxTask;
    new_time_plan_activity?: (TimePlanActivity | null);
};


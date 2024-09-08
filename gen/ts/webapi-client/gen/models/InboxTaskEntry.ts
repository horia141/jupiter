/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { InboxTask } from './InboxTask';
import type { TimeEventInDayBlock } from './TimeEventInDayBlock';

/**
 * Result entry.
 */
export type InboxTaskEntry = {
    inbox_task: InboxTask;
    time_events: Array<TimeEventInDayBlock>;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { InboxTask } from './InboxTask';
import type { ScheduleEventInDay } from './ScheduleEventInDay';
import type { TimeEventInDayBlock } from './TimeEventInDayBlock';

/**
 * InDayBlockLoadResult.
 */
export type TimeEventInDayBlockLoadResult = {
    in_day_block: TimeEventInDayBlock;
    schedule_event?: (ScheduleEventInDay | null);
    inbox_task?: (InboxTask | null);
};


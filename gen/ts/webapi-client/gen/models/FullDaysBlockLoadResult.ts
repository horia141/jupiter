/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Person } from './Person';
import type { ScheduleEventFullDays } from './ScheduleEventFullDays';
import type { TimeEventFullDaysBlock } from './TimeEventFullDaysBlock';

/**
 * FullDaysBlockLoadResult.
 */
export type FullDaysBlockLoadResult = {
    full_days_block: TimeEventFullDaysBlock;
    schedule_event?: (ScheduleEventFullDays | null);
    person?: (Person | null);
};


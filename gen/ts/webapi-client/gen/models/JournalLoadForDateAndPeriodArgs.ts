/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';

/**
 * Args.
 */
export type JournalLoadForDateAndPeriodArgs = {
    right_now: ADate;
    period: RecurringTaskPeriod;
    allow_archived: boolean;
};


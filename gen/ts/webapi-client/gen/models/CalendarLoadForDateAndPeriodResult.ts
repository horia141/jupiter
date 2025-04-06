/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { CalendarEventsEntries } from './CalendarEventsEntries';
import type { CalendarEventsStats } from './CalendarEventsStats';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
/**
 * Result.
 */
export type CalendarLoadForDateAndPeriodResult = {
    right_now: ADate;
    period: RecurringTaskPeriod;
    stats_subperiod?: (RecurringTaskPeriod | null);
    period_start_date: ADate;
    period_end_date: ADate;
    prev_period_start_date: ADate;
    next_period_start_date: ADate;
    entries?: (CalendarEventsEntries | null);
    stats?: (CalendarEventsStats | null);
};


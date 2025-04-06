/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
/**
 * Args.
 */
export type CalendarLoadForDateAndPeriodArgs = {
    right_now: ADate;
    period: RecurringTaskPeriod;
    stats_subperiod?: (RecurringTaskPeriod | null);
};


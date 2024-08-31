/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CalendarEventsStatsPerSubperiod } from './CalendarEventsStatsPerSubperiod';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';

/**
 * Stats about events in a period.
 */
export type CalendarEventsStats = {
    subperiod: RecurringTaskPeriod;
    per_subperiod: Array<CalendarEventsStatsPerSubperiod>;
};


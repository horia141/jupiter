/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';

/**
 * Stats about a particular subperiod.
 */
export type CalendarEventsStatsPerSubperiod = {
    period_start_date: ADate;
    schedule_event_full_days_cnt: number;
    schedule_event_in_day_cnt: number;
    inbox_task_cnt: number;
    person_birthday_cnt: number;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { InboxTaskEntry } from './InboxTaskEntry';
import type { PersonEntry } from './PersonEntry';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { ScheduleFullDaysEventEntry } from './ScheduleFullDaysEventEntry';
import type { ScheduleInDayEventEntry } from './ScheduleInDayEventEntry';

/**
 * Result.
 */
export type CalendarLoadForDateAndPeriodResult = {
    right_now: ADate;
    period: RecurringTaskPeriod;
    prev_period_start_date: ADate;
    next_period_start_date: ADate;
    schedule_event_in_day_entries: Array<ScheduleInDayEventEntry>;
    schedule_event_full_days_entries: Array<ScheduleFullDaysEventEntry>;
    inbox_task_entries: Array<InboxTaskEntry>;
    person_entries: Array<PersonEntry>;
};


/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InboxTaskEntry } from './InboxTaskEntry';
import type { PersonEntry } from './PersonEntry';
import type { ScheduleFullDaysEventEntry } from './ScheduleFullDaysEventEntry';
import type { ScheduleInDayEventEntry } from './ScheduleInDayEventEntry';
import type { VacationEntry } from './VacationEntry';
/**
 * Full entries for results.
 */
export type CalendarEventsEntries = {
    schedule_event_full_days_entries: Array<ScheduleFullDaysEventEntry>;
    schedule_event_in_day_entries: Array<ScheduleInDayEventEntry>;
    inbox_task_entries: Array<InboxTaskEntry>;
    person_entries: Array<PersonEntry>;
    vacation_entries: Array<VacationEntry>;
};


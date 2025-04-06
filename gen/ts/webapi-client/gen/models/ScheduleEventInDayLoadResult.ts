/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Note } from './Note';
import type { ScheduleEventInDay } from './ScheduleEventInDay';
import type { TimeEventInDayBlock } from './TimeEventInDayBlock';
/**
 * Result.
 */
export type ScheduleEventInDayLoadResult = {
    schedule_event_in_day: ScheduleEventInDay;
    time_event_in_day_block: TimeEventInDayBlock;
    note?: (Note | null);
};


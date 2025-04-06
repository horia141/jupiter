/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Note } from './Note';
import type { ScheduleEventFullDays } from './ScheduleEventFullDays';
import type { TimeEventFullDaysBlock } from './TimeEventFullDaysBlock';
/**
 * Result.
 */
export type ScheduleEventFullDaysLoadResult = {
    schedule_event_full_days: ScheduleEventFullDays;
    time_event_full_days_block: TimeEventFullDaysBlock;
    note?: (Note | null);
};


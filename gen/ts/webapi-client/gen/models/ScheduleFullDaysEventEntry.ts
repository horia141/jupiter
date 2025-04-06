/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ScheduleEventFullDays } from './ScheduleEventFullDays';
import type { ScheduleStream } from './ScheduleStream';
import type { TimeEventFullDaysBlock } from './TimeEventFullDaysBlock';
/**
 * Result entry.
 */
export type ScheduleFullDaysEventEntry = {
    event: ScheduleEventFullDays;
    time_event: TimeEventFullDaysBlock;
    stream: ScheduleStream;
};


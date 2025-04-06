/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ScheduleEventInDay } from './ScheduleEventInDay';
import type { ScheduleStream } from './ScheduleStream';
import type { TimeEventInDayBlock } from './TimeEventInDayBlock';
/**
 * Result entry.
 */
export type ScheduleInDayEventEntry = {
    event: ScheduleEventInDay;
    time_event: TimeEventInDayBlock;
    stream: ScheduleStream;
};


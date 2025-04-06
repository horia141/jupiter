/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { ScheduleEventName } from './ScheduleEventName';
import type { TimeInDay } from './TimeInDay';
/**
 * Args.
 */
export type ScheduleEventInDayUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: ScheduleEventName;
    };
    start_date: {
        should_change: boolean;
        value?: ADate;
    };
    start_time_in_day: {
        should_change: boolean;
        value?: TimeInDay;
    };
    duration_mins: {
        should_change: boolean;
        value?: number;
    };
};


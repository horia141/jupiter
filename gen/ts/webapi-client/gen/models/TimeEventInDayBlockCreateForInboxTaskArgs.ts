/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { TimeInDay } from './TimeInDay';
/**
 * Args.
 */
export type TimeEventInDayBlockCreateForInboxTaskArgs = {
    inbox_task_ref_id: EntityId;
    start_date: ADate;
    start_time_in_day: TimeInDay;
    duration_mins: number;
};


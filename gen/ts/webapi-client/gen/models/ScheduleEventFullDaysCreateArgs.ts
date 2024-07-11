/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { ScheduleEventName } from './ScheduleEventName';

/**
 * Args.
 */
export type ScheduleEventFullDaysCreateArgs = {
    schedule_stream_ref_id: EntityId;
    name: ScheduleEventName;
    start_date: ADate;
    duration_days: number;
};


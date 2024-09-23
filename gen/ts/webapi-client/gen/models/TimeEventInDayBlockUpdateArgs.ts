/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { TimeInDay } from './TimeInDay';

/**
 * Args.
 */
export type TimeEventInDayBlockUpdateArgs = {
    ref_id: EntityId;
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

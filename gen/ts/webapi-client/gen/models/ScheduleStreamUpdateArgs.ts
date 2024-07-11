/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { ScheduleStreamColor } from './ScheduleStreamColor';
import type { ScheduleStreamName } from './ScheduleStreamName';

/**
 * Args.
 */
export type ScheduleStreamUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: ScheduleStreamName;
    };
    color: {
        should_change: boolean;
        value?: ScheduleStreamColor;
    };
};


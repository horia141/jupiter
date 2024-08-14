/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { ScheduleStreamColor } from './ScheduleStreamColor';
import type { ScheduleStreamName } from './ScheduleStreamName';

/**
 * Summary information about a schedule stream.
 */
export type ScheduleStreamSummary = {
    ref_id: EntityId;
    name: ScheduleStreamName;
    color: ScheduleStreamColor;
};


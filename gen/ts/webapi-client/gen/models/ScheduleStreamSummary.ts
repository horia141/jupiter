/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { ScheduleSource } from './ScheduleSource';
import type { ScheduleStreamColor } from './ScheduleStreamColor';
import type { ScheduleStreamName } from './ScheduleStreamName';
/**
 * Summary information about a schedule stream.
 */
export type ScheduleStreamSummary = {
    ref_id: EntityId;
    source: ScheduleSource;
    name: ScheduleStreamName;
    color: ScheduleStreamColor;
};


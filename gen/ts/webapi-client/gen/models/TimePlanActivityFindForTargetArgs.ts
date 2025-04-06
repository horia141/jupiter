/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { TimePlanActivityTarget } from './TimePlanActivityTarget';
/**
 * Args.
 */
export type TimePlanActivityFindForTargetArgs = {
    allow_archived: boolean;
    target: TimePlanActivityTarget;
    target_ref_id: EntityId;
};


/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
/**
 * Args.
 */
export type TimePlanLoadArgs = {
    ref_id: EntityId;
    allow_archived: boolean;
    include_targets: boolean;
    include_completed_nontarget: boolean;
    include_other_time_plans: boolean;
};


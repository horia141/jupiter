/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { TimePlanActivityFeasability } from './TimePlanActivityFeasability';
import type { TimePlanActivityKind } from './TimePlanActivityKind';
/**
 * Args.
 */
export type TimePlanAssociateBigPlanWithPlanArgs = {
    big_plan_ref_id: EntityId;
    time_plan_ref_ids: Array<EntityId>;
    kind: TimePlanActivityKind;
    feasability: TimePlanActivityFeasability;
};


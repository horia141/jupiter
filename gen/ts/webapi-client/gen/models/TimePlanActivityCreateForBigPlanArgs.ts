/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { TimePlanActivityFeasability } from './TimePlanActivityFeasability';
import type { TimePlanActivityKind } from './TimePlanActivityKind';

/**
 * Args.
 */
export type TimePlanActivityCreateForBigPlanArgs = {
    time_plan_ref_id: EntityId;
    big_plan_ref_id: EntityId;
    kind: TimePlanActivityKind;
    feasability: TimePlanActivityFeasability;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { BigPlanName } from './BigPlanName';
import type { EntityId } from './EntityId';

/**
 * The view of a big plan via a workable.
 */
export type WorkableBigPlan = {
    ref_id: EntityId;
    name: BigPlanName;
    actionable_date?: ADate;
};


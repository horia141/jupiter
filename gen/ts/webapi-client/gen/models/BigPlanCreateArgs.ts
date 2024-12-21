/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { BigPlanName } from './BigPlanName';
import type { EntityId } from './EntityId';

/**
 * Big plan create args.
 */
export type BigPlanCreateArgs = {
    name: BigPlanName;
    time_plan_ref_id?: (EntityId | null);
    project_ref_id?: (EntityId | null);
    actionable_date?: (ADate | null);
    due_date?: (ADate | null);
};


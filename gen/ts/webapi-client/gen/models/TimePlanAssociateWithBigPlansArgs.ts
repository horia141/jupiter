/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * Args.
 */
export type TimePlanAssociateWithBigPlansArgs = {
    ref_id: EntityId;
    big_plan_ref_ids: Array<EntityId>;
    override_existing_dates: boolean;
};


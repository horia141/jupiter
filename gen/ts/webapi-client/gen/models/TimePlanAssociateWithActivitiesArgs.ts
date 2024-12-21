/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * Args.
 */
export type TimePlanAssociateWithActivitiesArgs = {
    ref_id: EntityId;
    other_time_plan_ref_id: EntityId;
    activity_ref_ids: Array<EntityId>;
    override_existing_dates: boolean;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * Args.
 */
export type TimePlanAssociateWithInboxTasksArgs = {
    ref_id: EntityId;
    inbox_task_ref_ids: Array<EntityId>;
    override_existing_dates: boolean;
};


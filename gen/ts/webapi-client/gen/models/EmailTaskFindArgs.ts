/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * PersonFindArgs.
 */
export type EmailTaskFindArgs = {
    allow_archived: boolean;
    include_inbox_task: boolean;
    filter_ref_ids?: (Array<EntityId> | null);
};


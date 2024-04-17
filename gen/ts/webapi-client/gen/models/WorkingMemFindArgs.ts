/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * PersonFindArgs.
 */
export type WorkingMemFindArgs = {
    allow_archived: boolean;
    include_notes: boolean;
    include_cleanup_tasks: boolean;
    filter_ref_ids?: (Array<EntityId> | null);
};


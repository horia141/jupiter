/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * PersonFindArgs.
 */
export type ChoreFindArgs = {
    allow_archived: boolean;
    include_project: boolean;
    include_inbox_tasks: boolean;
    filter_ref_ids?: Array<EntityId>;
    filter_project_ref_ids?: Array<EntityId>;
};


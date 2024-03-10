/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * PersonFindArgs.
 */
export type VacationFindArgs = {
    allow_archived: boolean;
    include_notes: boolean;
    filter_ref_ids?: Array<EntityId>;
};


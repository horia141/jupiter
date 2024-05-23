/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * Args.
 */
export type TimePlanFindArgs = {
    allow_archived: boolean;
    include_notes: boolean;
    filter_ref_ids?: (Array<EntityId> | null);
};


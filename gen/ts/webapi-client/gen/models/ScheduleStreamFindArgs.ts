/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * Args.
 */
export type ScheduleStreamFindArgs = {
    include_notes: boolean;
    allow_archived: boolean;
    filter_ref_ids?: (Array<EntityId> | null);
};


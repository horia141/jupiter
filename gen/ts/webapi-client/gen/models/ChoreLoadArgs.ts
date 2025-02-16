/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * ChoreLoadArgs.
 */
export type ChoreLoadArgs = {
    ref_id: EntityId;
    allow_archived: boolean;
    inbox_task_retrieve_offset?: (number | null);
};


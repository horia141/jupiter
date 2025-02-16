/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * Working mem find args.
 */
export type WorkingMemLoadArgs = {
    ref_id: EntityId;
    allow_archived: boolean;
    cleanup_task_retrieve_offset?: (number | null);
};


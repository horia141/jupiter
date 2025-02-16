/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * MetricLoadArgs.
 */
export type MetricLoadArgs = {
    ref_id: EntityId;
    allow_archived: boolean;
    allow_archived_entries: boolean;
    collection_task_retrieve_offset?: (number | null);
};


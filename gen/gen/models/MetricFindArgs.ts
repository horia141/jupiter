/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * PersonFindArgs.
 */
export type MetricFindArgs = {
    allow_archived: boolean;
    include_entries: boolean;
    include_collection_inbox_tasks: boolean;
    include_metric_entry_notes: boolean;
    filter_ref_ids?: Array<EntityId>;
    filter_entry_ref_ids?: Array<EntityId>;
};


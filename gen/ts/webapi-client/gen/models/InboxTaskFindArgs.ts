/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { InboxTaskSource } from './InboxTaskSource';

/**
 * PersonFindArgs.
 */
export type InboxTaskFindArgs = {
    allow_archived: boolean;
    include_notes: boolean;
    filter_just_workable?: (boolean | null);
    filter_ref_ids?: (Array<EntityId> | null);
    filter_project_ref_ids?: (Array<EntityId> | null);
    filter_sources?: (Array<InboxTaskSource> | null);
};


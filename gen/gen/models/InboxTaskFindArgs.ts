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
    filter_ref_ids?: Array<EntityId>;
    filter_project_ref_ids?: Array<EntityId>;
    filter_sources?: Array<InboxTaskSource>;
};


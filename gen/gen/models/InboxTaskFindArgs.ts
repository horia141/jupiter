/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { InboxTaskSource } from './InboxTaskSource';

export type InboxTaskFindArgs = {
    allow_archived: boolean;
    filter_ref_ids?: Array<EntityId>;
    filter_project_ref_ids?: Array<EntityId>;
    filter_sources?: Array<InboxTaskSource>;
};


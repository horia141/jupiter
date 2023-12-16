/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

export type DocFindArgs = {
    include_notes: boolean;
    allow_archived: boolean;
    include_subdocs: boolean;
    filter_ref_ids?: Array<EntityId>;
};


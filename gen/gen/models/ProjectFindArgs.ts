/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

export type ProjectFindArgs = {
    allow_archived: boolean;
    filter_ref_ids?: Array<EntityId>;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

export type NoteFindArgs = {
    allow_archived: boolean;
    include_subnotes: boolean;
    filter_ref_ids?: Array<EntityId>;
};


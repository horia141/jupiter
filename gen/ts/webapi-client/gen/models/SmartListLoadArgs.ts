/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

/**
 * SmartListLoadArgs.
 */
export type SmartListLoadArgs = {
    ref_id: EntityId;
    allow_archived: boolean;
    allow_archived_items: boolean;
    allow_archived_tags: boolean;
};


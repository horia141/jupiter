/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { TagName } from './TagName';

/**
 * PersonFindArgs.
 */
export type SmartListFindArgs = {
    allow_archived: boolean;
    include_notes: boolean;
    include_tags: boolean;
    include_items: boolean;
    include_item_notes: boolean;
    filter_ref_ids?: Array<EntityId>;
    filter_is_done?: boolean;
    filter_tag_names?: Array<TagName>;
    filter_tag_ref_id?: Array<EntityId>;
    filter_item_ref_id?: Array<EntityId>;
};


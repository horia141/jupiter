/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { SmartListTagName } from './SmartListTagName';
export type SmartListFindArgs = {
    allow_archived: boolean;
    include_tags: boolean;
    include_items: boolean;
    filter_ref_ids: Array<EntityId>;
    filter_is_done: boolean;
    filter_tag_names: Array<SmartListTagName>;
    filter_tag_ref_id: Array<EntityId>;
    filter_item_ref_id: Array<EntityId>;
};


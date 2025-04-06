/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { SmartListItemName } from './SmartListItemName';
import type { TagName } from './TagName';
import type { URL } from './URL';
/**
 * SmartListItemCreate args.
 */
export type SmartListItemCreateArgs = {
    smart_list_ref_id: EntityId;
    name: SmartListItemName;
    is_done: boolean;
    tag_names: Array<TagName>;
    url?: (URL | null);
};


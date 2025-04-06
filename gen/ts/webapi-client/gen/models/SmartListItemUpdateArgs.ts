/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { SmartListItemName } from './SmartListItemName';
import type { TagName } from './TagName';
import type { URL } from './URL';
/**
 * PersonFindArgs.
 */
export type SmartListItemUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: SmartListItemName;
    };
    is_done: {
        should_change: boolean;
        value?: boolean;
    };
    tags: {
        should_change: boolean;
        value?: Array<TagName>;
    };
    url: {
        should_change: boolean;
        value?: (URL | null);
    };
};


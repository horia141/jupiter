/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { SmartListTagName } from './SmartListTagName';
/**
 * PersonFindArgs.
 */
export type SmartListTagUpdateArgs = {
    ref_id: EntityId;
    tag_name: {
        should_change: boolean;
        value?: SmartListTagName;
    };
};


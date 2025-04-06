/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { SmartListName } from './SmartListName';
/**
 * Summary information about a smart list.
 */
export type SmartListSummary = {
    ref_id: EntityId;
    name: SmartListName;
    icon?: (EntityIcon | null);
};


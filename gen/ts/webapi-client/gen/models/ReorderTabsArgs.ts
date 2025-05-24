/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { HomeTabTarget } from './HomeTabTarget';
/**
 * The arguments for reordering tabs in the home config.
 */
export type ReorderTabsArgs = {
    target: HomeTabTarget;
    order_of_tabs: Array<EntityId>;
};


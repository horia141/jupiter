/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
/**
 * A tab on the home page.
 */
export type HomeMobileTabConfig = {
    name: EntityName;
    icon?: (EntityIcon | null);
    widgets: Array<Array<EntityId>>;
};


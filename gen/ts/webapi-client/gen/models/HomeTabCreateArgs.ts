/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityIcon } from './EntityIcon';
import type { EntityName } from './EntityName';
import type { HomeTabTarget } from './HomeTabTarget';
/**
 * The arguments for the create home tab use case.
 */
export type HomeTabCreateArgs = {
    target: HomeTabTarget;
    name: EntityName;
    icon?: (EntityIcon | null);
};


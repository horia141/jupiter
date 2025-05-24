/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
/**
 * The arguments for updating a home tab.
 */
export type HomeTabUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: EntityName;
    };
    icon: {
        should_change: boolean;
        value?: (EntityIcon | null);
    };
};


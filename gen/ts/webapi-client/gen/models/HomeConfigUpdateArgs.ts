/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
/**
 * The arguments for updating the home config.
 */
export type HomeConfigUpdateArgs = {
    key_habits: {
        should_change: boolean;
        value?: (Array<EntityId> | null);
    };
    key_metrics: {
        should_change: boolean;
        value?: (Array<EntityId> | null);
    };
};


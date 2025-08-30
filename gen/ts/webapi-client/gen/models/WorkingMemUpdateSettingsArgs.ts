/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
/**
 * PersonFindArgs.
 */
export type WorkingMemUpdateSettingsArgs = {
    generation_period: {
        should_change: boolean;
        value?: RecurringTaskPeriod;
    };
    cleanup_project_ref_id: {
        should_change: boolean;
        value?: EntityId;
    };
};


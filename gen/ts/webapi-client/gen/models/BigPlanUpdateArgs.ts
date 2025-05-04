/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { BigPlanName } from './BigPlanName';
import type { BigPlanStatus } from './BigPlanStatus';
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityId } from './EntityId';
/**
 * PersonFindArgs.
 */
export type BigPlanUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: BigPlanName;
    };
    status: {
        should_change: boolean;
        value?: BigPlanStatus;
    };
    project_ref_id: {
        should_change: boolean;
        value?: EntityId;
    };
    is_key: {
        should_change: boolean;
        value?: boolean;
    };
    eisen: {
        should_change: boolean;
        value?: Eisen;
    };
    difficulty: {
        should_change: boolean;
        value?: Difficulty;
    };
    actionable_date: {
        should_change: boolean;
        value?: (ADate | null);
    };
    due_date: {
        should_change: boolean;
        value?: (ADate | null);
    };
};


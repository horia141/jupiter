/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { TimePlanActivityFeasability } from './TimePlanActivityFeasability';
import type { TimePlanActivityKind } from './TimePlanActivityKind';
/**
 * TimePlanActivityFindArgs.
 */
export type TimePlanActivityUpdateArgs = {
    ref_id: EntityId;
    kind: {
        should_change: boolean;
        value?: TimePlanActivityKind;
    };
    feasability: {
        should_change: boolean;
        value?: TimePlanActivityFeasability;
    };
};


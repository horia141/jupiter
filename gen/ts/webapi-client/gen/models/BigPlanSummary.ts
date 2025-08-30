/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BigPlanName } from './BigPlanName';
import type { EntityId } from './EntityId';
/**
 * Summary information about a big plan.
 */
export type BigPlanSummary = {
    ref_id: EntityId;
    name: BigPlanName;
    project_ref_id: EntityId;
    is_key: boolean;
};


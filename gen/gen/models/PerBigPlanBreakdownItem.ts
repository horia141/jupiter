/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { BigPlanWorkSummary } from './BigPlanWorkSummary';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
export type PerBigPlanBreakdownItem = {
    ref_id: EntityId;
    name: EntityName;
    actionable_date: ADate;
    summary: BigPlanWorkSummary;
};


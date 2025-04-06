/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { RecurringTaskWorkSummary } from './RecurringTaskWorkSummary';
/**
 * The report for a particular chore.
 */
export type PerChoreBreakdownItem = {
    ref_id: EntityId;
    name: EntityName;
    suspended: boolean;
    archived: boolean;
    period: RecurringTaskPeriod;
    summary: RecurringTaskWorkSummary;
};


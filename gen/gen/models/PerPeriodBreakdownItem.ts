/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityName } from './EntityName';
import type { InboxTasksSummary } from './InboxTasksSummary';
import type { WorkableSummary } from './WorkableSummary';
/**
 * The report for a particular time period.
 */
export type PerPeriodBreakdownItem = {
    name: EntityName;
    inbox_tasks_summary: InboxTasksSummary;
    big_plans_summary: WorkableSummary;
};


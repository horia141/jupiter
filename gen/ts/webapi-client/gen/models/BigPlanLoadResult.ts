/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BigPlan } from './BigPlan';
import type { BigPlanStats } from './BigPlanStats';
import type { InboxTask } from './InboxTask';
import type { Note } from './Note';
import type { Project } from './Project';
/**
 * BigPlanLoadResult.
 */
export type BigPlanLoadResult = {
    big_plan: BigPlan;
    project: Project;
    inbox_tasks: Array<InboxTask>;
    note?: (Note | null);
    stats: BigPlanStats;
};


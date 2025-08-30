/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BigPlan } from './BigPlan';
import type { BigPlanMilestone } from './BigPlanMilestone';
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
    milestones: Array<BigPlanMilestone>;
    inbox_tasks: Array<InboxTask>;
    note?: (Note | null);
    stats: BigPlanStats;
};


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
 * A single big plan result.
 */
export type BigPlanFindResultEntry = {
    big_plan: BigPlan;
    note?: (Note | null);
    milestones?: (Array<BigPlanMilestone> | null);
    stats?: (BigPlanStats | null);
    project?: (Project | null);
    inbox_tasks?: (Array<InboxTask> | null);
};


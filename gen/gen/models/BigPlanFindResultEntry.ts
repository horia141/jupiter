/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BigPlan } from './BigPlan';
import type { InboxTask } from './InboxTask';
import type { Project } from './Project';
export type BigPlanFindResultEntry = {
    big_plan: BigPlan;
    project?: Project;
    inbox_tasks?: Array<InboxTask>;
};


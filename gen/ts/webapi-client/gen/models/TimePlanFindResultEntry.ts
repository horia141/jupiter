/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InboxTask } from './InboxTask';
import type { Note } from './Note';
import type { TimePlan } from './TimePlan';
/**
 * Result part.
 */
export type TimePlanFindResultEntry = {
    time_plan: TimePlan;
    note?: (Note | null);
    planning_task?: (InboxTask | null);
};


/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Habit } from './Habit';
import type { InboxTask } from './InboxTask';
import type { Project } from './Project';
/**
 * HabitLoadResult.
 */
export type HabitLoadResult = {
    habit: Habit;
    project: Project;
    inbox_tasks: Array<InboxTask>;
};


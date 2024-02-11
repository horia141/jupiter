/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Habit } from './Habit';
import type { InboxTask } from './InboxTask';
import type { Project } from './Project';
/**
 * A single entry in the load all habits response.
 */
export type HabitFindResultEntry = {
    habit: Habit;
    project?: Project;
    inbox_tasks?: Array<InboxTask>;
};


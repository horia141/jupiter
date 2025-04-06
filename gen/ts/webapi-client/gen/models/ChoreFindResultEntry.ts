/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Chore } from './Chore';
import type { InboxTask } from './InboxTask';
import type { Note } from './Note';
import type { Project } from './Project';
/**
 * A single entry in the load all chores response.
 */
export type ChoreFindResultEntry = {
    chore: Chore;
    note?: (Note | null);
    project?: (Project | null);
    inbox_tasks?: (Array<InboxTask> | null);
};


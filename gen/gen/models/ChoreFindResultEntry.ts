/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Chore } from './Chore';
import type { InboxTask } from './InboxTask';
import type { Project } from './Project';
export type ChoreFindResultEntry = {
    chore: Chore;
    project?: Project;
    inbox_tasks?: Array<InboxTask>;
};


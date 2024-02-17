/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Chore } from './Chore';
import type { InboxTask } from './InboxTask';
import type { Project } from './Project';

/**
 * ChoreLoadResult.
 */
export type ChoreLoadResult = {
    chore: Chore;
    project: Project;
    inbox_tasks: Array<InboxTask>;
};


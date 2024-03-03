/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Chore } from './Chore';
import type { InboxTask } from './InboxTask';
import type { Project } from './Project';

/**
 * A single entry in the load all chores response.
 */
export type ChoreFindResultEntry = {
    chore: Chore;
    project?: Project;
    inbox_tasks?: Array<InboxTask>;
};


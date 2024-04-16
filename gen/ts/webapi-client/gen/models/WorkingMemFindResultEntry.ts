/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { InboxTask } from './InboxTask';
import type { Note } from './Note';
import type { WorkingMem } from './WorkingMem';

/**
 * PersonFindResult object.
 */
export type WorkingMemFindResultEntry = {
    working_mem: WorkingMem;
    note?: Note;
    cleanup_task?: InboxTask;
};


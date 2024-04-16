/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { InboxTask } from './InboxTask';
import type { Note } from './Note';
import type { WorkingMem } from './WorkingMem';

/**
 * Working mem load  result.
 */
export type WorkingMemLoadResult = {
    working_mem: WorkingMem;
    note: Note;
    cleanup_task: InboxTask;
};


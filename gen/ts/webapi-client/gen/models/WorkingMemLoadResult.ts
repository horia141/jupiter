/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { InboxTask } from './InboxTask';
import type { Note } from './Note';
import type { WorkingMem } from './WorkingMem';

/**
 * Working mem load result.
 */
export type WorkingMemLoadResult = {
    working_mem: WorkingMem;
    note: Note;
    cleanup_tasks: Array<InboxTask>;
    cleanup_tasks_total_cnt: number;
    cleanup_tasks_page_size: number;
};


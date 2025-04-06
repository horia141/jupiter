/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InboxTask } from './InboxTask';
import type { Note } from './Note';
import type { WorkingMem } from './WorkingMem';
/**
 * Working mem load current entry.
 */
export type WorkingMemLoadCurrentEntry = {
    working_mem: WorkingMem;
    note: Note;
    cleanup_task: InboxTask;
};


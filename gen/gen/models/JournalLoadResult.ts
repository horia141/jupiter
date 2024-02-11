/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InboxTask } from './InboxTask';
import type { Journal } from './Journal';
import type { Note } from './Note';
/**
 * Result.
 */
export type JournalLoadResult = {
    journal: Journal;
    note: Note;
    writing_task?: InboxTask;
};


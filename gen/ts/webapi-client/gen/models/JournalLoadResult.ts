/* generated using openapi-typescript-codegen -- do not edit */
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
    writing_task?: (InboxTask | null);
    sub_period_journals: Array<Journal>;
};


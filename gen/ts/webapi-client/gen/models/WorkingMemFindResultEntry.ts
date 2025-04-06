/* generated using openapi-typescript-codegen -- do not edit */
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
    note?: (Note | null);
    cleanup_task?: (InboxTask | null);
};


/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { RecurringTaskGenParams } from './RecurringTaskGenParams';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { Timestamp } from './Timestamp';
/**
 * A journal.
 */
export type JournalCollection = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: Timestamp;
    workspace: string;
    periods: Array<RecurringTaskPeriod>;
    writing_task_project_ref_id: EntityId;
    writing_task_gen_params: RecurringTaskGenParams;
};


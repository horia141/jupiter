/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityId } from './EntityId';
import type { InboxTaskName } from './InboxTaskName';
import type { InboxTaskSource } from './InboxTaskSource';
import type { InboxTaskStatus } from './InboxTaskStatus';
import type { Timestamp } from './Timestamp';
/**
 * An inbox task.
 */
export type InboxTask = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: InboxTaskName;
    inbox_task_collection_ref_id: string;
    source: InboxTaskSource;
    project_ref_id: EntityId;
    status: InboxTaskStatus;
    eisen: Eisen;
    difficulty: Difficulty;
    actionable_date?: (ADate | null);
    due_date?: (ADate | null);
    notes?: (string | null);
    source_entity_ref_id?: (EntityId | null);
    recurring_timeline?: (string | null);
    recurring_repeat_index?: (number | null);
    recurring_gen_right_now?: (Timestamp | null);
    working_time?: (Timestamp | null);
    completed_time?: (Timestamp | null);
};


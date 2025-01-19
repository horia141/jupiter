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
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: InboxTaskName;
    inbox_task_collection_ref_id: string;
    source: InboxTaskSource;
    project_ref_id: EntityId;
    status: InboxTaskStatus;
    eisen: Eisen;
    difficulty?: (Difficulty | null);
    actionable_date?: (ADate | null);
    due_date?: (ADate | null);
    notes?: (string | null);
    working_mem_ref_id?: (EntityId | null);
    habit_ref_id?: (EntityId | null);
    chore_ref_id?: (EntityId | null);
    big_plan_ref_id?: (EntityId | null);
    journal_ref_id?: (EntityId | null);
    metric_ref_id?: (EntityId | null);
    person_ref_id?: (EntityId | null);
    slack_task_ref_id?: (EntityId | null);
    email_task_ref_id?: (EntityId | null);
    recurring_timeline?: (string | null);
    recurring_repeat_index?: (number | null);
    recurring_gen_right_now?: (Timestamp | null);
    working_time?: (Timestamp | null);
    completed_time?: (Timestamp | null);
};


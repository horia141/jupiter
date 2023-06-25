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

export type InboxTask = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    inbox_task_collection_ref_id: EntityId;
    source: InboxTaskSource;
    project_ref_id: EntityId;
    name: InboxTaskName;
    status: InboxTaskStatus;
    eisen: Eisen;
    difficulty?: Difficulty;
    actionable_date?: ADate;
    due_date?: ADate;
    notes?: string;
    big_plan_ref_id?: EntityId;
    habit_ref_id?: EntityId;
    chore_ref_id?: EntityId;
    metric_ref_id?: EntityId;
    person_ref_id?: EntityId;
    slack_task_ref_id?: EntityId;
    email_task_ref_id?: EntityId;
    recurring_timeline?: string;
    recurring_repeat_index?: number;
    recurring_gen_right_now?: Timestamp;
    accepted_time?: Timestamp;
    working_time?: Timestamp;
    completed_time?: Timestamp;
};


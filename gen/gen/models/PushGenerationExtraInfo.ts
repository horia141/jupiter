/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { InboxTaskName } from './InboxTaskName';
import type { InboxTaskStatus } from './InboxTaskStatus';
import type { Timezone } from './Timezone';
export type PushGenerationExtraInfo = {
    timezone: Timezone;
    name?: InboxTaskName;
    status?: InboxTaskStatus;
    eisen?: Eisen;
    difficulty?: Difficulty;
    actionable_date?: ADate;
    due_date?: ADate;
};


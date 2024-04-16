/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { InboxTaskName } from './InboxTaskName';
import type { InboxTaskStatus } from './InboxTaskStatus';
import type { Timezone } from './Timezone';

/**
 * Extra information for how to generate an inbox task.
 */
export type PushGenerationExtraInfo = {
    timezone: Timezone;
    name?: InboxTaskName;
    status?: InboxTaskStatus;
    eisen?: Eisen;
    difficulty?: Difficulty;
    actionable_date?: ADate;
    due_date?: ADate;
};


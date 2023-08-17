/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityName } from './EntityName';
import type { InboxTaskStatus } from './InboxTaskStatus';
import type { Timezone } from './Timezone';

export type PushGenerationExtraInfo = {
    timezone: Timezone;
    name?: EntityName;
    status?: InboxTaskStatus;
    eisen?: Eisen;
    difficulty?: Difficulty;
    actionable_date?: ADate;
    due_date?: ADate;
};


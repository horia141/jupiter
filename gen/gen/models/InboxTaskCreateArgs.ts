/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';

export type InboxTaskCreateArgs = {
    name: EntityName;
    project_ref_id?: EntityId;
    big_plan_ref_id?: EntityId;
    eisen?: Eisen;
    difficulty?: Difficulty;
    actionable_date?: ADate;
    due_date?: ADate;
};


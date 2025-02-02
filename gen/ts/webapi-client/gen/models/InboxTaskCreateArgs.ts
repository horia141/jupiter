/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityId } from './EntityId';
import type { InboxTaskName } from './InboxTaskName';
import type { TimePlanActivityFeasability } from './TimePlanActivityFeasability';
import type { TimePlanActivityKind } from './TimePlanActivityKind';

/**
 * InboxTaskCreate args.
 */
export type InboxTaskCreateArgs = {
    name: InboxTaskName;
    time_plan_ref_id?: (EntityId | null);
    time_plan_activity_kind?: (TimePlanActivityKind | null);
    time_plan_activity_feasability?: (TimePlanActivityFeasability | null);
    project_ref_id?: (EntityId | null);
    big_plan_ref_id?: (EntityId | null);
    eisen: Eisen;
    difficulty: Difficulty;
    actionable_date?: (ADate | null);
    due_date?: (ADate | null);
};


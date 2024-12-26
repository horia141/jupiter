/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { SyncTarget } from './SyncTarget';

/**
 * PersonFindArgs.
 */
export type GenDoArgs = {
    gen_even_if_not_modified: boolean;
    today?: (ADate | null);
    gen_targets?: (Array<SyncTarget> | null);
    period?: (Array<RecurringTaskPeriod> | null);
    filter_project_ref_ids?: (Array<EntityId> | null);
    filter_habit_ref_ids?: (Array<EntityId> | null);
    filter_chore_ref_ids?: (Array<EntityId> | null);
    filter_metric_ref_ids?: (Array<EntityId> | null);
    filter_person_ref_ids?: (Array<EntityId> | null);
    filter_slack_task_ref_ids?: (Array<EntityId> | null);
    filter_email_task_ref_ids?: (Array<EntityId> | null);
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EventSource } from './EventSource';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { SyncTarget } from './SyncTarget';

/**
 * PersonFindArgs.
 */
export type GenDoArgs = {
    source: EventSource;
    gen_even_if_not_modified: boolean;
    today?: ADate;
    gen_targets?: Array<SyncTarget>;
    period?: Array<RecurringTaskPeriod>;
    filter_project_ref_ids?: Array<EntityId>;
    filter_habit_ref_ids?: Array<EntityId>;
    filter_chore_ref_ids?: Array<EntityId>;
    filter_metric_ref_ids?: Array<EntityId>;
    filter_person_ref_ids?: Array<EntityId>;
    filter_slack_task_ref_ids?: Array<EntityId>;
    filter_email_task_ref_ids?: Array<EntityId>;
};


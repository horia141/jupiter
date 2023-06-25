/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { InboxTaskSource } from './InboxTaskSource';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';

export type ReportArgs = {
    today: ADate;
    period: RecurringTaskPeriod;
    filter_project_ref_ids?: Array<EntityId>;
    filter_sources?: Array<InboxTaskSource>;
    filter_big_plan_ref_ids?: Array<EntityId>;
    filter_habit_ref_ids?: Array<EntityId>;
    filter_chore_ref_ids?: Array<EntityId>;
    filter_metric_ref_ids?: Array<EntityId>;
    filter_person_ref_ids?: Array<EntityId>;
    filter_slack_task_ref_ids?: Array<EntityId>;
    filter_email_task_ref_ids?: Array<EntityId>;
    breakdown_period?: RecurringTaskPeriod;
};


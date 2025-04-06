/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { InboxTaskSource } from './InboxTaskSource';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { ReportBreakdown } from './ReportBreakdown';
/**
 * Report args.
 */
export type ReportArgs = {
    today?: (ADate | null);
    period: RecurringTaskPeriod;
    sources?: (Array<InboxTaskSource> | null);
    breakdowns?: (Array<ReportBreakdown> | null);
    filter_project_ref_ids?: (Array<EntityId> | null);
    filter_big_plan_ref_ids?: (Array<EntityId> | null);
    filter_habit_ref_ids?: (Array<EntityId> | null);
    filter_chore_ref_ids?: (Array<EntityId> | null);
    filter_metric_ref_ids?: (Array<EntityId> | null);
    filter_person_ref_ids?: (Array<EntityId> | null);
    filter_slack_task_ref_ids?: (Array<EntityId> | null);
    filter_email_task_ref_ids?: (Array<EntityId> | null);
    breakdown_period?: (RecurringTaskPeriod | null);
};


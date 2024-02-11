/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { InboxTaskSource } from './InboxTaskSource';
import type { InboxTasksSummary } from './InboxTasksSummary';
import type { PerBigPlanBreakdownItem } from './PerBigPlanBreakdownItem';
import type { PerChoreBreakdownItem } from './PerChoreBreakdownItem';
import type { PerHabitBreakdownItem } from './PerHabitBreakdownItem';
import type { PerPeriodBreakdownItem } from './PerPeriodBreakdownItem';
import type { PerProjectBreakdownItem } from './PerProjectBreakdownItem';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { ReportBreakdown } from './ReportBreakdown';
import type { UserScoreOverview } from './UserScoreOverview';
import type { WorkableSummary } from './WorkableSummary';
/**
 * Report result.
 */
export type ReportPeriodResult = {
    today: ADate;
    period: RecurringTaskPeriod;
    sources: Array<InboxTaskSource>;
    breakdowns: Array<ReportBreakdown>;
    breakdown_period?: RecurringTaskPeriod;
    global_inbox_tasks_summary: InboxTasksSummary;
    global_big_plans_summary: WorkableSummary;
    per_project_breakdown: Array<PerProjectBreakdownItem>;
    per_period_breakdown: Array<PerPeriodBreakdownItem>;
    per_habit_breakdown: Array<PerHabitBreakdownItem>;
    per_chore_breakdown: Array<PerChoreBreakdownItem>;
    per_big_plan_breakdown: Array<PerBigPlanBreakdownItem>;
    user_score_overview?: UserScoreOverview;
};


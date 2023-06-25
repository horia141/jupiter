/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { InboxTasksSummary } from './InboxTasksSummary';
import type { PerBigPlanBreakdownItem } from './PerBigPlanBreakdownItem';
import type { PerChoreBreakdownItem } from './PerChoreBreakdownItem';
import type { PerHabitBreakdownItem } from './PerHabitBreakdownItem';
import type { PerPeriodBreakdownItem } from './PerPeriodBreakdownItem';
import type { PerProjectBreakdownItem } from './PerProjectBreakdownItem';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { WorkableSummary } from './WorkableSummary';

export type ReportResult = {
    today: ADate;
    period: RecurringTaskPeriod;
    global_inbox_tasks_summary: InboxTasksSummary;
    global_big_plans_summary: WorkableSummary;
    per_project_breakdown: Array<PerProjectBreakdownItem>;
    per_period_breakdown: Array<PerPeriodBreakdownItem>;
    per_habit_breakdown: Array<PerHabitBreakdownItem>;
    per_chore_breakdown: Array<PerChoreBreakdownItem>;
    per_big_plan_breakdown: Array<PerBigPlanBreakdownItem>;
};


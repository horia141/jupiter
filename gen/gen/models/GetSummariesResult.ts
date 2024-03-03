/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BigPlanSummary } from './BigPlanSummary';
import type { ChoreSummary } from './ChoreSummary';
import type { HabitSummary } from './HabitSummary';
import type { InboxTaskSummary } from './InboxTaskSummary';
import type { MetricSummary } from './MetricSummary';
import type { PersonSummary } from './PersonSummary';
import type { ProjectSummary } from './ProjectSummary';
import type { SmartListSummary } from './SmartListSummary';
import type { VacationSummary } from './VacationSummary';

/**
 * Get summaries result.
 */
export type GetSummariesResult = {
    default_project?: ProjectSummary;
    vacations?: Array<VacationSummary>;
    projects?: Array<ProjectSummary>;
    inbox_tasks?: Array<InboxTaskSummary>;
    habits?: Array<HabitSummary>;
    chores?: Array<ChoreSummary>;
    big_plans?: Array<BigPlanSummary>;
    smart_lists?: Array<SmartListSummary>;
    metrics?: Array<MetricSummary>;
    persons?: Array<PersonSummary>;
};


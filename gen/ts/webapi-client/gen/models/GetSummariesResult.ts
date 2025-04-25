/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BigPlanSummary } from './BigPlanSummary';
import type { ChoreSummary } from './ChoreSummary';
import type { HabitSummary } from './HabitSummary';
import type { InboxTaskSummary } from './InboxTaskSummary';
import type { JournalSummary } from './JournalSummary';
import type { MetricSummary } from './MetricSummary';
import type { PersonSummary } from './PersonSummary';
import type { ProjectSummary } from './ProjectSummary';
import type { ScheduleStreamSummary } from './ScheduleStreamSummary';
import type { SmartListSummary } from './SmartListSummary';
import type { VacationSummary } from './VacationSummary';
import type { Workspace } from './Workspace';
/**
 * Get summaries result.
 */
export type GetSummariesResult = {
    workspace?: (Workspace | null);
    vacations?: (Array<VacationSummary> | null);
    schedule_streams?: (Array<ScheduleStreamSummary> | null);
    root_project?: (ProjectSummary | null);
    projects?: (Array<ProjectSummary> | null);
    inbox_tasks?: (Array<InboxTaskSummary> | null);
    journals_last_year?: (Array<JournalSummary> | null);
    habits?: (Array<HabitSummary> | null);
    chores?: (Array<ChoreSummary> | null);
    big_plans?: (Array<BigPlanSummary> | null);
    smart_lists?: (Array<SmartListSummary> | null);
    metrics?: (Array<MetricSummary> | null);
    persons?: (Array<PersonSummary> | null);
};


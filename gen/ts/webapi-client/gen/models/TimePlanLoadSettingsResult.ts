/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Project } from './Project';
import type { RecurringTaskGenParams } from './RecurringTaskGenParams';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { TimePlanGenerationApproach } from './TimePlanGenerationApproach';
/**
 * TimePlanLoadSettingsResult.
 */
export type TimePlanLoadSettingsResult = {
    periods: Array<RecurringTaskPeriod>;
    generation_approach: TimePlanGenerationApproach;
    generation_in_advance_days: Record<string, number>;
    planning_task_project?: (Project | null);
    planning_task_gen_params?: (RecurringTaskGenParams | null);
};


/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Project } from './Project';
import type { RecurringTaskGenParams } from './RecurringTaskGenParams';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
export type JournalLoadSettingsResult = {
    periods: Array<RecurringTaskPeriod>;
    writing_task_project: Project;
    writing_task_gen_params: RecurringTaskGenParams;
};


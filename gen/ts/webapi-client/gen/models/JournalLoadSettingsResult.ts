/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InboxTask } from './InboxTask';
import type { JournalGenerationApproach } from './JournalGenerationApproach';
import type { Project } from './Project';
import type { RecurringTaskGenParams } from './RecurringTaskGenParams';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
/**
 * JournalLoadSettings results.
 */
export type JournalLoadSettingsResult = {
    periods: Array<RecurringTaskPeriod>;
    generation_approach: JournalGenerationApproach;
    generation_in_advance_days: Record<string, number>;
    writing_task_project?: (Project | null);
    writing_task_gen_params?: (RecurringTaskGenParams | null);
    writing_tasks: Array<InboxTask>;
};


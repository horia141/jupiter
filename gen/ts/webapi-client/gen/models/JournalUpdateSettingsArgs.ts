/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityId } from './EntityId';
import type { JournalGenerationApproach } from './JournalGenerationApproach';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
/**
 * Args.
 */
export type JournalUpdateSettingsArgs = {
    periods: {
        should_change: boolean;
        value?: Array<RecurringTaskPeriod>;
    };
    generation_approach: {
        should_change: boolean;
        value?: JournalGenerationApproach;
    };
    generation_in_advance_days: {
        should_change: boolean;
        value?: Record<string, number>;
    };
    writing_task_project_ref_id: {
        should_change: boolean;
        value?: (EntityId | null);
    };
    writing_task_eisen: {
        should_change: boolean;
        value?: (Eisen | null);
    };
    writing_task_difficulty: {
        should_change: boolean;
        value?: (Difficulty | null);
    };
};


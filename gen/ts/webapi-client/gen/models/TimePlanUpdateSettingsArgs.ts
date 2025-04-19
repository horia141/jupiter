/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityId } from './EntityId';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { TimePlanGenerationApproach } from './TimePlanGenerationApproach';
/**
 * Args.
 */
export type TimePlanUpdateSettingsArgs = {
    periods: {
        should_change: boolean;
        value?: Array<RecurringTaskPeriod>;
    };
    generation_approach: {
        should_change: boolean;
        value?: TimePlanGenerationApproach;
    };
    planning_task_project_ref_id: {
        should_change: boolean;
        value?: (EntityId | null);
    };
    planning_task_eisen: {
        should_change: boolean;
        value?: (Eisen | null);
    };
    planning_task_difficulty: {
        should_change: boolean;
        value?: (Difficulty | null);
    };
};


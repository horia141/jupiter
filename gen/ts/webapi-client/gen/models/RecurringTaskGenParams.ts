/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { RecurringTaskDueAtDay } from './RecurringTaskDueAtDay';
import type { RecurringTaskDueAtMonth } from './RecurringTaskDueAtMonth';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { RecurringTaskSkipRule } from './RecurringTaskSkipRule';
/**
 * Parameters for metric collection.
 */
export type RecurringTaskGenParams = {
    period: RecurringTaskPeriod;
    eisen: Eisen;
    difficulty: Difficulty;
    actionable_from_day?: (RecurringTaskDueAtDay | null);
    actionable_from_month?: (RecurringTaskDueAtMonth | null);
    due_at_day?: (RecurringTaskDueAtDay | null);
    due_at_month?: (RecurringTaskDueAtMonth | null);
    skip_rule?: (RecurringTaskSkipRule | null);
};


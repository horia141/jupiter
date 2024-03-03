/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { RecurringTaskDueAtDay } from './RecurringTaskDueAtDay';
import type { RecurringTaskDueAtMonth } from './RecurringTaskDueAtMonth';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';

/**
 * Parameters for metric collection.
 */
export type RecurringTaskGenParams = {
    period: RecurringTaskPeriod;
    eisen?: Eisen;
    difficulty?: Difficulty;
    actionable_from_day?: RecurringTaskDueAtDay;
    actionable_from_month?: RecurringTaskDueAtMonth;
    due_at_day?: RecurringTaskDueAtDay;
    due_at_month?: RecurringTaskDueAtMonth;
};


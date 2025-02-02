/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityId } from './EntityId';
import type { HabitName } from './HabitName';
import type { RecurringTaskDueAtDay } from './RecurringTaskDueAtDay';
import type { RecurringTaskDueAtMonth } from './RecurringTaskDueAtMonth';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { RecurringTaskSkipRule } from './RecurringTaskSkipRule';

/**
 * HabitCreate args..
 */
export type HabitCreateArgs = {
    name: HabitName;
    period: RecurringTaskPeriod;
    project_ref_id?: (EntityId | null);
    eisen: Eisen;
    difficulty: Difficulty;
    actionable_from_day?: (RecurringTaskDueAtDay | null);
    actionable_from_month?: (RecurringTaskDueAtMonth | null);
    due_at_day?: (RecurringTaskDueAtDay | null);
    due_at_month?: (RecurringTaskDueAtMonth | null);
    skip_rule?: (RecurringTaskSkipRule | null);
    repeats_in_period_count?: (number | null);
};


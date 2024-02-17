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
    project_ref_id?: EntityId;
    eisen?: Eisen;
    difficulty?: Difficulty;
    actionable_from_day?: RecurringTaskDueAtDay;
    actionable_from_month?: RecurringTaskDueAtMonth;
    due_at_day?: RecurringTaskDueAtDay;
    due_at_month?: RecurringTaskDueAtMonth;
    skip_rule?: RecurringTaskSkipRule;
    repeats_in_period_count?: number;
};


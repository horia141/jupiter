/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { ChoreName } from './ChoreName';
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityId } from './EntityId';
import type { RecurringTaskDueAtDay } from './RecurringTaskDueAtDay';
import type { RecurringTaskDueAtMonth } from './RecurringTaskDueAtMonth';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { RecurringTaskSkipRule } from './RecurringTaskSkipRule';

/**
 * ChoreCreate args.
 */
export type ChoreCreateArgs = {
    name: ChoreName;
    period: RecurringTaskPeriod;
    project_ref_id?: (EntityId | null);
    eisen: Eisen;
    difficulty: Difficulty;
    actionable_from_day?: (RecurringTaskDueAtDay | null);
    actionable_from_month?: (RecurringTaskDueAtMonth | null);
    due_at_day?: (RecurringTaskDueAtDay | null);
    due_at_month?: (RecurringTaskDueAtMonth | null);
    must_do: boolean;
    skip_rule?: (RecurringTaskSkipRule | null);
    start_at_date?: (ADate | null);
    end_at_date?: (ADate | null);
};


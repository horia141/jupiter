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
 * PersonFindArgs.
 */
export type ChoreUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: ChoreName;
    };
    period: {
        should_change: boolean;
        value?: RecurringTaskPeriod;
    };
    eisen: {
        should_change: boolean;
        value?: (Eisen | null);
    };
    difficulty: {
        should_change: boolean;
        value?: (Difficulty | null);
    };
    actionable_from_day: {
        should_change: boolean;
        value?: (RecurringTaskDueAtDay | null);
    };
    actionable_from_month: {
        should_change: boolean;
        value?: (RecurringTaskDueAtMonth | null);
    };
    due_at_day: {
        should_change: boolean;
        value?: (RecurringTaskDueAtDay | null);
    };
    due_at_month: {
        should_change: boolean;
        value?: (RecurringTaskDueAtMonth | null);
    };
    must_do: {
        should_change: boolean;
        value?: boolean;
    };
    skip_rule: {
        should_change: boolean;
        value?: (RecurringTaskSkipRule | null);
    };
    start_at_date: {
        should_change: boolean;
        value?: ADate;
    };
    end_at_date: {
        should_change: boolean;
        value?: (ADate | null);
    };
};


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
import type { RecurringTaskDueAtTime } from './RecurringTaskDueAtTime';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { RecurringTaskSkipRule } from './RecurringTaskSkipRule';

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
        value?: Eisen;
    };
    difficulty: {
        should_change: boolean;
        value?: Difficulty;
    };
    actionable_from_day: {
        should_change: boolean;
        value?: RecurringTaskDueAtDay;
    };
    actionable_from_month: {
        should_change: boolean;
        value?: RecurringTaskDueAtMonth;
    };
    due_at_time: {
        should_change: boolean;
        value?: RecurringTaskDueAtTime;
    };
    due_at_day: {
        should_change: boolean;
        value?: RecurringTaskDueAtDay;
    };
    due_at_month: {
        should_change: boolean;
        value?: RecurringTaskDueAtMonth;
    };
    must_do: {
        should_change: boolean;
        value?: boolean;
    };
    skip_rule: {
        should_change: boolean;
        value?: RecurringTaskSkipRule;
    };
    start_at_date: {
        should_change: boolean;
        value?: ADate;
    };
    end_at_date: {
        should_change: boolean;
        value?: ADate;
    };
};


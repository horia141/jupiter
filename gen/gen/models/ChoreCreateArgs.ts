/* generated using openapi-typescript-codegen -- do no edit */
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
export type ChoreCreateArgs = {
    name: ChoreName;
    period: RecurringTaskPeriod;
    project_ref_id: EntityId;
    eisen: Eisen;
    difficulty: Difficulty;
    actionable_from_day: RecurringTaskDueAtDay;
    actionable_from_month: RecurringTaskDueAtMonth;
    due_at_time: RecurringTaskDueAtTime;
    due_at_day: RecurringTaskDueAtDay;
    due_at_month: RecurringTaskDueAtMonth;
    must_do: boolean;
    skip_rule: RecurringTaskSkipRule;
    start_at_date: ADate;
    end_at_date: ADate;
};


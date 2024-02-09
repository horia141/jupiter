/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { RecurringTaskDueAtDay } from './RecurringTaskDueAtDay';
import type { RecurringTaskDueAtMonth } from './RecurringTaskDueAtMonth';
import type { RecurringTaskDueAtTime } from './RecurringTaskDueAtTime';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
export type MetricUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: EntityName;
    };
    icon: {
        should_change: boolean;
        value?: EntityIcon;
    };
    collection_period: {
        should_change: boolean;
        value?: RecurringTaskPeriod;
    };
    collection_eisen: {
        should_change: boolean;
        value?: Eisen;
    };
    collection_difficulty: {
        should_change: boolean;
        value?: Difficulty;
    };
    collection_actionable_from_day: {
        should_change: boolean;
        value?: RecurringTaskDueAtDay;
    };
    collection_actionable_from_month: {
        should_change: boolean;
        value?: RecurringTaskDueAtMonth;
    };
    collection_due_at_time: {
        should_change: boolean;
        value?: RecurringTaskDueAtTime;
    };
    collection_due_at_day: {
        should_change: boolean;
        value?: RecurringTaskDueAtDay;
    };
    collection_due_at_month: {
        should_change: boolean;
        value?: RecurringTaskDueAtMonth;
    };
};


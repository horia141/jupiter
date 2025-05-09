/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { MetricName } from './MetricName';
import type { RecurringTaskDueAtDay } from './RecurringTaskDueAtDay';
import type { RecurringTaskDueAtMonth } from './RecurringTaskDueAtMonth';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
/**
 * PersonFindArgs.
 */
export type MetricUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: MetricName;
    };
    is_key: {
        should_change: boolean;
        value?: boolean;
    };
    icon: {
        should_change: boolean;
        value?: (EntityIcon | null);
    };
    collection_period: {
        should_change: boolean;
        value?: (RecurringTaskPeriod | null);
    };
    collection_eisen: {
        should_change: boolean;
        value?: (Eisen | null);
    };
    collection_difficulty: {
        should_change: boolean;
        value?: (Difficulty | null);
    };
    collection_actionable_from_day: {
        should_change: boolean;
        value?: (RecurringTaskDueAtDay | null);
    };
    collection_actionable_from_month: {
        should_change: boolean;
        value?: (RecurringTaskDueAtMonth | null);
    };
    collection_due_at_day: {
        should_change: boolean;
        value?: (RecurringTaskDueAtDay | null);
    };
    collection_due_at_month: {
        should_change: boolean;
        value?: (RecurringTaskDueAtMonth | null);
    };
};


/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityIcon } from './EntityIcon';
import type { MetricName } from './MetricName';
import type { MetricUnit } from './MetricUnit';
import type { RecurringTaskDueAtDay } from './RecurringTaskDueAtDay';
import type { RecurringTaskDueAtMonth } from './RecurringTaskDueAtMonth';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
/**
 * PersonFindArgs.
 */
export type MetricCreateArgs = {
    name: MetricName;
    is_key: boolean;
    icon?: (EntityIcon | null);
    collection_period?: (RecurringTaskPeriod | null);
    collection_eisen?: (Eisen | null);
    collection_difficulty?: (Difficulty | null);
    collection_actionable_from_day?: (RecurringTaskDueAtDay | null);
    collection_actionable_from_month?: (RecurringTaskDueAtMonth | null);
    collection_due_at_day?: (RecurringTaskDueAtDay | null);
    collection_due_at_month?: (RecurringTaskDueAtMonth | null);
    metric_unit?: (MetricUnit | null);
};


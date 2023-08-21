/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityIcon } from './EntityIcon';
import type { EntityName } from './EntityName';
import type { MetricUnit } from './MetricUnit';
import type { RecurringTaskDueAtDay } from './RecurringTaskDueAtDay';
import type { RecurringTaskDueAtMonth } from './RecurringTaskDueAtMonth';
import type { RecurringTaskDueAtTime } from './RecurringTaskDueAtTime';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';

export type MetricCreateArgs = {
    name: EntityName;
    icon?: EntityIcon;
    collection_period?: RecurringTaskPeriod;
    collection_eisen?: Eisen;
    collection_difficulty?: Difficulty;
    collection_actionable_from_day?: RecurringTaskDueAtDay;
    collection_actionable_from_month?: RecurringTaskDueAtMonth;
    collection_due_at_time?: RecurringTaskDueAtTime;
    collection_due_at_day?: RecurringTaskDueAtDay;
    collection_due_at_month?: RecurringTaskDueAtMonth;
    metric_unit?: MetricUnit;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { RecurringTaskWorkSummary } from './RecurringTaskWorkSummary';

export type PerHabitBreakdownItem = {
    ref_id: EntityId;
    name: EntityName;
    archived: boolean;
    period: RecurringTaskPeriod;
    suspended: boolean;
    summary: RecurringTaskWorkSummary;
};


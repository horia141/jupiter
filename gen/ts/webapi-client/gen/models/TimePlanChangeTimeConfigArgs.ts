/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';

/**
 * Args.
 */
export type TimePlanChangeTimeConfigArgs = {
    ref_id: EntityId;
    right_now: {
        should_change: boolean;
        value?: ADate;
    };
    period: {
        should_change: boolean;
        value?: RecurringTaskPeriod;
    };
};


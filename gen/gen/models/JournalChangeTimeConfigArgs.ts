/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';

export type JournalChangeTimeConfigArgs = {
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


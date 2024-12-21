/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Note } from './Note';
import type { TimePlan } from './TimePlan';

/**
 * Result part.
 */
export type TimePlanFindResultEntry = {
    time_plan: TimePlan;
    note?: (Note | null);
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Note } from './Note';
import type { TimePlan } from './TimePlan';

/**
 * Result.
 */
export type TimePlanCreateResult = {
    new_time_plan: TimePlan;
    new_note: Note;
};


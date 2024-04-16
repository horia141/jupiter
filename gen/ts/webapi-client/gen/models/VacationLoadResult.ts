/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Note } from './Note';
import type { Vacation } from './Vacation';

/**
 * VacationLoadResult.
 */
export type VacationLoadResult = {
    vacation: Vacation;
    note?: Note;
};


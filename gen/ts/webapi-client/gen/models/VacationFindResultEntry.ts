/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Note } from './Note';
import type { Vacation } from './Vacation';

/**
 * PersonFindResult object.
 */
export type VacationFindResultEntry = {
    vacation: Vacation;
    note?: (Note | null);
};


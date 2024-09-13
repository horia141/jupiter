/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { TimeEventFullDaysBlock } from './TimeEventFullDaysBlock';
import type { Vacation } from './Vacation';

/**
 * Result entry.
 */
export type VacationEntry = {
    vacation: Vacation;
    time_event: TimeEventFullDaysBlock;
};


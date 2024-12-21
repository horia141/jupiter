/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { TimeEventFullDaysBlock } from './TimeEventFullDaysBlock';
import type { Vacation } from './Vacation';

/**
 * Vacation creation result.
 */
export type VacationCreateResult = {
    new_vacation: Vacation;
    new_time_event_block: TimeEventFullDaysBlock;
};


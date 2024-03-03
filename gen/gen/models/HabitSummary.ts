/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { HabitName } from './HabitName';

/**
 * Summary information about a habit.
 */
export type HabitSummary = {
    ref_id: EntityId;
    name: HabitName;
};


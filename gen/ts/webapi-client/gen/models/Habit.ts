/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { HabitName } from './HabitName';
import type { RecurringTaskGenParams } from './RecurringTaskGenParams';
import type { RecurringTaskSkipRule } from './RecurringTaskSkipRule';
import type { Timestamp } from './Timestamp';

/**
 * A habit.
 */
export type Habit = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: HabitName;
    habit_collection_ref_id: string;
    project_ref_id: EntityId;
    gen_params: RecurringTaskGenParams;
    skip_rule?: (RecurringTaskSkipRule | null);
    suspended: boolean;
    repeats_in_period_count?: (number | null);
};


/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { HabitName } from './HabitName';
import type { HabitRepeatsStrategy } from './HabitRepeatsStrategy';
import type { RecurringTaskGenParams } from './RecurringTaskGenParams';
import type { Timestamp } from './Timestamp';
/**
 * A habit.
 */
export type Habit = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: HabitName;
    habit_collection_ref_id: string;
    project_ref_id: EntityId;
    is_key: boolean;
    gen_params: RecurringTaskGenParams;
    suspended: boolean;
    repeats_strategy?: (HabitRepeatsStrategy | null);
    repeats_in_period_count?: (number | null);
};


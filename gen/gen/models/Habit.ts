/* generated using openapi-typescript-codegen -- do no edit */
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
    archived_time?: Timestamp;
    name: HabitName;
    habit_collection: string;
    project_ref_id: EntityId;
    gen_params: RecurringTaskGenParams;
    skip_rule?: RecurringTaskSkipRule;
    suspended: boolean;
    repeats_in_period_count?: number;
};


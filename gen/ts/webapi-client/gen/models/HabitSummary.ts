/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { HabitName } from './HabitName';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
/**
 * Summary information about a habit.
 */
export type HabitSummary = {
    ref_id: EntityId;
    name: HabitName;
    is_key: boolean;
    period: RecurringTaskPeriod;
    project_ref_id: EntityId;
};


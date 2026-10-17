/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityId } from './EntityId';
import type { HabitName } from './HabitName';
import type { HabitRepeatsStrategy } from './HabitRepeatsStrategy';
import type { RecurringTaskDueAtDay } from './RecurringTaskDueAtDay';
import type { RecurringTaskDueAtMonth } from './RecurringTaskDueAtMonth';
import type { RecurringTaskSkipRule } from './RecurringTaskSkipRule';
import type { Schedulability } from './Schedulability';
/**
 * PersonFindArgs.
 */
export type HabitUpdateArgs = {
    ref_id: EntityId;
    name: {
        should_change: boolean;
        value?: HabitName;
    };
    aspect_ref_id: {
        should_change: boolean;
        value?: EntityId;
    };
    chapter_ref_id: {
        should_change: boolean;
        value?: (EntityId | null);
    };
    goal_ref_id: {
        should_change: boolean;
        value?: (EntityId | null);
    };
    stack_ref_id: {
        should_change: boolean;
        value?: (EntityId | null);
    };
    is_key: {
        should_change: boolean;
        value?: boolean;
    };
    eisen: {
        should_change: boolean;
        value?: Eisen;
    };
    difficulty: {
        should_change: boolean;
        value?: Difficulty;
    };
    actionable_from_day: {
        should_change: boolean;
        value?: (RecurringTaskDueAtDay | null);
    };
    actionable_from_month: {
        should_change: boolean;
        value?: (RecurringTaskDueAtMonth | null);
    };
    due_at_day: {
        should_change: boolean;
        value?: (RecurringTaskDueAtDay | null);
    };
    due_at_month: {
        should_change: boolean;
        value?: (RecurringTaskDueAtMonth | null);
    };
    skip_rule: {
        should_change: boolean;
        value?: (RecurringTaskSkipRule | null);
    };
    repeats_strategy: {
        should_change: boolean;
        value?: (HabitRepeatsStrategy | null);
    };
    repeats_in_period_count: {
        should_change: boolean;
        value?: (number | null);
    };
    schedulability: {
        should_change: boolean;
        value?: Schedulability;
    };
    scheduling_event_duration_mins: {
        should_change: boolean;
        value?: (number | null);
    };
    scheduling_event_count: {
        should_change: boolean;
        value?: (number | null);
    };
    suspended: {
        should_change: boolean;
        value?: boolean;
    };
};


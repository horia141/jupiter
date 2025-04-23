/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { BigPlanName } from './BigPlanName';
import type { Difficulty } from './Difficulty';
import type { Eisen } from './Eisen';
import type { EntityId } from './EntityId';
import type { TimePlanActivityFeasability } from './TimePlanActivityFeasability';
import type { TimePlanActivityKind } from './TimePlanActivityKind';
/**
 * Big plan create args.
 */
export type BigPlanCreateArgs = {
    name: BigPlanName;
    time_plan_ref_id?: (EntityId | null);
    time_plan_activity_kind?: (TimePlanActivityKind | null);
    time_plan_activity_feasability?: (TimePlanActivityFeasability | null);
    eisen: Eisen;
    difficulty: Difficulty;
    project_ref_id?: (EntityId | null);
    actionable_date?: (ADate | null);
    due_date?: (ADate | null);
};


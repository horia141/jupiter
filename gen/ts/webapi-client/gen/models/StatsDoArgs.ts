/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { SyncTarget } from './SyncTarget';
/**
 * StatsDoArgs.
 */
export type StatsDoArgs = {
    today?: (ADate | null);
    stats_targets?: (Array<SyncTarget> | null);
    filter_habit_ref_ids?: (Array<EntityId> | null);
    filter_big_plan_ref_ids?: (Array<EntityId> | null);
    filter_journal_ref_ids?: (Array<EntityId> | null);
};


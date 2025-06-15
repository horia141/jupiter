/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
/**
 * PersonFindArgs.
 */
export type BigPlanFindArgs = {
    allow_archived: boolean;
    include_project: boolean;
    include_inbox_tasks: boolean;
    include_notes: boolean;
    include_milestones: boolean;
    include_stats: boolean;
    filter_just_workable?: (boolean | null);
    filter_ref_ids?: (Array<EntityId> | null);
    filter_project_ref_ids?: (Array<EntityId> | null);
};


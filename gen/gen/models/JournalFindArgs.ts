/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
/**
 * Args.
 */
export type JournalFindArgs = {
    allow_archived: boolean;
    include_notes: boolean;
    include_writing_tasks: boolean;
    filter_ref_ids?: Array<EntityId>;
};


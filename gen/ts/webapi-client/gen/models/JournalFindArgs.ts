/* generated using openapi-typescript-codegen -- do not edit */
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
    include_journal_stats: boolean;
    include_writing_tasks: boolean;
    filter_ref_ids?: (Array<EntityId> | null);
};


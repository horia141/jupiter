/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { RecurringTaskPeriod } from './RecurringTaskPeriod';
import type { Timestamp } from './Timestamp';
/**
 * The working memory log.
 */
export type WorkingMemCollection = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    workspace_ref_id: string;
    generation_period: RecurringTaskPeriod;
    cleanup_project_ref_id: EntityId;
};


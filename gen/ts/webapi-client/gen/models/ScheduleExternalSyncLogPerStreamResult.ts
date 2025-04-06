/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
/**
 * The result of syncing a stream.
 */
export type ScheduleExternalSyncLogPerStreamResult = {
    schedule_stream_ref_id: EntityId;
    success: boolean;
    error_msg?: (string | null);
};


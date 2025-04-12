/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { Timestamp } from './Timestamp';
/**
 * A metric entry.
 */
export type MetricEntry = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    metric_ref_id: string;
    collection_time: ADate;
    value: number;
};


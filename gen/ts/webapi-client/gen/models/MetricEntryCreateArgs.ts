/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
/**
 * MetricEntryCreate args.
 */
export type MetricEntryCreateArgs = {
    metric_ref_id: EntityId;
    value: number;
    collection_time?: (ADate | null);
};


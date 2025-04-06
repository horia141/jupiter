/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
/**
 * PersonFindArgs.
 */
export type MetricEntryUpdateArgs = {
    ref_id: EntityId;
    collection_time: {
        should_change: boolean;
        value?: ADate;
    };
    value: {
        should_change: boolean;
        value?: number;
    };
};


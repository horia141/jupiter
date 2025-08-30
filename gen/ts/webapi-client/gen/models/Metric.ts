/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { MetricName } from './MetricName';
import type { MetricUnit } from './MetricUnit';
import type { RecurringTaskGenParams } from './RecurringTaskGenParams';
import type { Timestamp } from './Timestamp';
/**
 * A metric.
 */
export type Metric = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: MetricName;
    metric_collection_ref_id: string;
    is_key: boolean;
    icon?: (EntityIcon | null);
    collection_params?: (RecurringTaskGenParams | null);
    metric_unit?: (MetricUnit | null);
};


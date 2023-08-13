/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { Timestamp } from './Timestamp';

export type MetricEntry = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: EntityName;
    metric_ref_id: EntityId;
    collection_time: ADate;
    value: number;
    notes: string;
};


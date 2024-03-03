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
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: Timestamp;
    name: MetricName;
    metric_collection: string;
    icon?: EntityIcon;
    collection_params?: RecurringTaskGenParams;
    metric_unit?: MetricUnit;
};


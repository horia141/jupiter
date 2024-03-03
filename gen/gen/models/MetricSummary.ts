/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { MetricName } from './MetricName';

/**
 * Summary information about a metric.
 */
export type MetricSummary = {
    ref_id: EntityId;
    name: MetricName;
    icon?: EntityIcon;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { MetricName } from './MetricName';

export type MetricSummary = {
    ref_id: EntityId;
    name: MetricName;
    icon?: EntityIcon;
};


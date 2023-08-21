/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';

export type MetricSummary = {
    ref_id: EntityId;
    name: EntityName;
    icon?: EntityIcon;
};


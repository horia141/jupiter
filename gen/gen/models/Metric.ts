/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { MetricUnit } from './MetricUnit';
import type { ParentLink } from './ParentLink';
import type { RecurringTaskGenParams } from './RecurringTaskGenParams';
import type { Timestamp } from './Timestamp';
export type Metric = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: EntityName;
    metric_collection: ParentLink;
    icon?: EntityIcon;
    collection_params?: RecurringTaskGenParams;
    metric_unit?: MetricUnit;
};


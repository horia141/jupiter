/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InboxTask } from './InboxTask';
import type { Metric } from './Metric';
import type { MetricEntry } from './MetricEntry';
/**
 * MetricLoadResult.
 */
export type MetricLoadResult = {
    metric: Metric;
    metric_entries: Array<MetricEntry>;
    metric_collection_inbox_tasks: Array<InboxTask>;
};


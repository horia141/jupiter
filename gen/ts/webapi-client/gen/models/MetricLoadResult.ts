/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { InboxTask } from './InboxTask';
import type { Metric } from './Metric';
import type { MetricEntry } from './MetricEntry';
import type { Note } from './Note';

/**
 * MetricLoadResult.
 */
export type MetricLoadResult = {
    metric: Metric;
    note?: (Note | null);
    metric_entries: Array<MetricEntry>;
    metric_collection_inbox_tasks: Array<InboxTask>;
};


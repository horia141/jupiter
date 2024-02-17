/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { InboxTask } from './InboxTask';
import type { Metric } from './Metric';
import type { MetricEntry } from './MetricEntry';
import type { Note } from './Note';

/**
 * A single entry in the LoadAllMetricsResponse.
 */
export type MetricFindResponseEntry = {
    metric: Metric;
    metric_entries?: Array<MetricEntry>;
    metric_collection_inbox_tasks?: Array<InboxTask>;
    metric_entry_notes?: Array<Note>;
};


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
    collection_tasks: Array<InboxTask>;
    collection_tasks_total_cnt: number;
    collection_tasks_page_size: number;
};


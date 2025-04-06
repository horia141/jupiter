/* generated using openapi-typescript-codegen -- do not edit */
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
    note?: (Note | null);
    metric_entries?: (Array<MetricEntry> | null);
    metric_collection_inbox_tasks?: (Array<InboxTask> | null);
    metric_entry_notes?: (Array<Note> | null);
};


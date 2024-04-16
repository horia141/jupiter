import type { MetricEntry } from "webapi-client";
import { aDateToDate } from "./adate";

export function metricEntryName(metricEntry: MetricEntry) {
  return `${metricEntry.value} at ${aDateToDate(
    metricEntry.collection_time
  ).toFormat("yyyy-MM-dd")}`;
}

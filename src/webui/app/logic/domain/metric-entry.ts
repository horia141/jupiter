import type { MetricEntry } from "jupiter-gen";
import { aDateToDate } from "./adate";

export function metricEntryName(metricEntry: MetricEntry) {
  return {
    the_name: `${metricEntry.value} at ${aDateToDate(
      metricEntry.collection_time
    ).toFormat("yyyy-MM-dd")}`,
  };
}

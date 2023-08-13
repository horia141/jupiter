import { Timestamp } from "jupiter-gen";
import { DateTime } from "luxon";

export function timestampToDate(timestamp: Timestamp): DateTime {
  const datetime = DateTime.fromISO(timestamp.the_ts);
  return DateTime.fromObject({
    year: datetime.year,
    month: datetime.month,
    day: datetime.day,
  });
}

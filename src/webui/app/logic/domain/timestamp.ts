import type { Timestamp } from "webapi-client";
import { DateTime } from "luxon";

export function timestampToDate(timestamp: Timestamp): DateTime {
  const datetime = DateTime.fromISO(timestamp);
  return DateTime.fromObject({
    year: datetime.year,
    month: datetime.month,
    day: datetime.day,
  });
}

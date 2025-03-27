import type { ADate } from "@jupiter/webapi-client";
import { DateTime } from "luxon";

export function aDateToDate(aDate: ADate): DateTime<true> {
  const date = DateTime.fromISO(aDate);
  if (!date.isValid) {
    throw new Error(`Invalid date: ${aDate}`);
  }
  return date;
}

export function compareADate(
  adate1?: ADate | null,
  adate2?: ADate | null,
): number {
  if (
    (adate1 === undefined || adate1 === null) &&
    (adate2 === undefined || adate2 === null)
  ) {
    return 0;
  } else if (adate1 === undefined || adate1 === null) {
    return 1;
  } else if (adate2 === undefined || adate2 === null) {
    return -1;
  } else {
    const iso1 = aDateToDate(adate1).toISO();
    const iso2 = aDateToDate(adate2).toISO();
    if (iso1 === iso2) {
      return 0;
    }
    return iso1 > iso2 ? 1 : -1;
  }
}

export function allDaysBetween(start: ADate, end: ADate): ADate[] {
  const startDate = aDateToDate(start);
  const endDate = aDateToDate(end);
  const days = [];
  for (let date = startDate; date <= endDate; date = date.plus({ days: 1 })) {
    days.push(date.toISODate());
  }
  return days;
}

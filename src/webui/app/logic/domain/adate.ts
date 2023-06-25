import type { ADate } from "jupiter-gen";
import { DateTime } from "luxon";

export function aDateToDate(aDate: ADate): DateTime {
  if (aDate.the_date) {
    return DateTime.fromISO(aDate.the_date);
  } else if (aDate.the_datetime) {
    return DateTime.fromISO(aDate.the_datetime);
  } else {
    throw Error("Invalid ADate object with no date nor datetime");
  }
}

export function compareADate(adate1?: ADate, adate2?: ADate): number {
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

import type { ADate, TimePlan } from "@jupiter/webapi-client";

import { aDateToDate, compareADate } from "~/logic/domain/adate";
import { comparePeriods } from "~/logic/domain/period";

export function findTimePlansThatAreActive(
  timePlans: Array<TimePlan>,
  today: ADate,
): TimePlan[] {
  const todayDate = aDateToDate(today);
  return timePlans.filter((timePlan) => {
    const startDate = aDateToDate(timePlan.start_date);
    const endDate = aDateToDate(timePlan.end_date);
    return startDate <= todayDate && todayDate <= endDate;
  });
}

export function sortTimePlansNaturally(timePlans: Array<TimePlan>): TimePlan[] {
  return [...timePlans].sort((j1, j2) => {
    if (j2.archived && !j1.archived) {
      return -1;
    }

    if (j1.archived && !j2.archived) {
      return 1;
    }

    return (
      -1 * compareADate(j1.right_now, j2.right_now) ||
      comparePeriods(j1.period, j2.period)
    );
  });
}

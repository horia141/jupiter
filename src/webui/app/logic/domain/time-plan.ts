import type { TimePlan } from "@jupiter/webapi-client";
import { TimePlanSource } from "@jupiter/webapi-client";
import { compareADate } from "./adate";
import { comparePeriods } from "./period";

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

export function timePlanSourceName(source: TimePlanSource) {
  switch (source) {
    case TimePlanSource.USER:
      return "User";
    case TimePlanSource.RECURRING:
      return "Recurring";
  }
}

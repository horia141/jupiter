import type { Journal } from "@jupiter/webapi-client";

import { compareADate } from "~/logic/domain/adate";
import { comparePeriods } from "~/logic/domain/period";

export function sortJournalsNaturally(journals: Array<Journal>): Journal[] {
  return [...journals].sort((j1, j2) => {
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

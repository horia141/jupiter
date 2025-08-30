import type { WorkingMem } from "@jupiter/webapi-client";

import { aDateToDate } from "~/logic/domain/adate";

export function sortWorkingMemsNaturally(workingMems: WorkingMem[]) {
  return [...workingMems].sort((v1, v2) => {
    const v1Start = aDateToDate(v1.right_now).toISO();
    const v2Start = aDateToDate(v2.right_now).toISO();
    if (v1Start !== v2Start) {
      return v1Start < v2Start ? 1 : -1;
    }

    return 0;
  });
}

import type { Vacation } from "jupiter-gen";
import { aDateToDate } from "./adate";

export function sortVacationsNaturally(vacations: Vacation[]) {
  return [...vacations].sort((v1, v2) => {
    const v1Start = aDateToDate(v1.start_date).toISO();
    const v2Start = aDateToDate(v2.start_date).toISO();
    if (v1Start !== v2Start) {
      return v1Start < v2Start ? 1 : -1;
    }

    const v1End = aDateToDate(v1.end_date).toISO();
    const v2End = aDateToDate(v2.end_date).toISO();
    if (v1End !== v2End) {
      return v1End < v2End ? 1 : -1;
    }

    return 0;
  });
}

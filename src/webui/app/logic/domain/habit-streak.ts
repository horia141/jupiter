import { ADate, EntityId, HabitStreakMark } from "@jupiter/webapi-client";

import { aDateToDate } from "~/logic/domain/adate";

export interface KeyHabitStreak {
  habitRefId: EntityId;
  streakMarkEarliestDate: ADate;
  streakMarkLatestDate: ADate;
  streakMarks: HabitStreakMark[];
}

export function limitKeyHabitResultsBasedOnScreenSize(
  keyHabitStreaks: KeyHabitStreak[],
  daysToRestrict: number,
): KeyHabitStreak[] {
  return keyHabitStreaks.map((h) => {
    const latestDate = h.streakMarkLatestDate;
    const realEarliestDate = aDateToDate(latestDate)
      .minus({ days: daysToRestrict })
      .toISODate();

    return {
      ...h,
      streakMarkEarliestDate: realEarliestDate,
      streakMarks: h.streakMarks.filter((s) => s.date >= realEarliestDate),
    };
  });
}

import { Difficulty, Eisen, type Habit } from "@jupiter/webapi-client";
import { compareDifficulty } from "./difficulty";
import { compareEisen } from "./eisen";
import { comparePeriods } from "./period";

export function sortHabitsNaturally(habits: Habit[]): Habit[] {
  return [...habits].sort((c1, c2) => {
    if (!c1.suspended && c2.suspended) {
      return -1;
    } else if (c1.suspended && !c2.suspended) {
      return 1;
    }

    return (
      comparePeriods(c1.gen_params.period, c2.gen_params.period) ||
      compareEisen(
        c1.gen_params.eisen ?? Eisen.REGULAR,
        c2.gen_params.eisen ?? Eisen.REGULAR
      ) ||
      compareDifficulty(
        c1.gen_params.difficulty ?? Difficulty.EASY,
        c2.gen_params.difficulty ?? Difficulty.EASY
      )
    );
  });
}

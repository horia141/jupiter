import { type Chore, Difficulty, Eisen } from "@jupiter/webapi-client";

import { compareDifficulty } from "~/logic/domain/difficulty";
import { compareEisen } from "~/logic/domain/eisen";
import { comparePeriods } from "~/logic/domain/period";

export function sortChoresNaturally(chores: Chore[]): Chore[] {
  return [...chores].sort((c1, c2) => {
    if (!c1.suspended && c2.suspended) {
      return -1;
    } else if (c1.suspended && !c2.suspended) {
      return 1;
    }

    return (
      comparePeriods(c1.gen_params.period, c2.gen_params.period) ||
      compareEisen(
        c1.gen_params.eisen ?? Eisen.REGULAR,
        c2.gen_params.eisen ?? Eisen.REGULAR,
      ) ||
      compareDifficulty(
        c1.gen_params.difficulty ?? Difficulty.EASY,
        c2.gen_params.difficulty ?? Difficulty.EASY,
      )
    );
  });
}

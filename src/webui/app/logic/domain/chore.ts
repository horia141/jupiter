import { type Chore } from "@jupiter/webapi-client";

import { compareDifficulty } from "~/logic/domain/difficulty";
import { compareEisen } from "~/logic/domain/eisen";
import { comparePeriods } from "~/logic/domain/period";
import { compareIsKey } from "~/logic/domain/is-key";

export function sortChoresNaturally(chores: Chore[]): Chore[] {
  return [...chores].sort((c1, c2) => {
    if (!c1.suspended && c2.suspended) {
      return -1;
    } else if (c1.suspended && !c2.suspended) {
      return 1;
    }

    return (
      compareIsKey(c1.is_key, c2.is_key) ||
      comparePeriods(c1.gen_params.period, c2.gen_params.period) ||
      compareEisen(c1.gen_params.eisen, c2.gen_params.eisen) ||
      compareDifficulty(c1.gen_params.difficulty, c2.gen_params.difficulty)
    );
  });
}

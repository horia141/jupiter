import type {
  BigPlan,
  BigPlanFindResultEntry,
  Project,
} from "@jupiter/webapi-client";

import { compareADate } from "./adate";
import { compareBigPlanStatus } from "./big-plan-status";
import { compareDifficulty } from "./difficulty";
import { compareEisen } from "./eisen";

export interface BigPlanParent {
  project?: Project;
}

export function bigPlanFindEntryToParent(
  entry: BigPlanFindResultEntry,
): BigPlanParent {
  return {
    project: entry.project || undefined,
  };
}

export function sortBigPlansNaturally(
  bigPlans: Array<BigPlan>,
): Array<BigPlan> {
  return [...bigPlans].sort((e1, e2) => {
    return (
      compareADate(e1.actionable_date, e2.actionable_date) ||
      compareADate(e1.due_date, e2.due_date) ||
      -1 * compareEisen(e1.eisen, e2.eisen) ||
      -1 * compareDifficulty(e1.difficulty, e2.difficulty) ||
      compareBigPlanStatus(e1.status, e2.status)
    );
  });
}

import {
  BigPlanStats,
  BigPlanStatus,
  type BigPlan,
  type BigPlanFindResultEntry,
  type Project,
} from "@jupiter/webapi-client";

import { compareADate } from "~/logic/domain/adate";
import { compareBigPlanStatus } from "~/logic/domain/big-plan-status";
import { compareDifficulty } from "~/logic/domain/difficulty";
import { compareEisen } from "~/logic/domain/eisen";
import { compareIsKey } from "~/logic/domain/is-key";
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
      compareIsKey(e1.is_key, e2.is_key) ||
      compareADate(e1.due_date, e2.due_date) ||
      -1 * compareEisen(e1.eisen, e2.eisen) ||
      -1 * compareDifficulty(e1.difficulty, e2.difficulty) ||
      compareBigPlanStatus(e1.status, e2.status)
    );
  });
}

export function bigPlanDonePct(
  bigPlan: BigPlan,
  bigPlanStats: BigPlanStats,
): number {
  if (bigPlan.status === BigPlanStatus.NOT_STARTED) {
    return 0;
  }

  if (
    bigPlan.status === BigPlanStatus.DONE ||
    bigPlan.status === BigPlanStatus.NOT_DONE
  ) {
    return 100;
  }

  if (bigPlanStats.all_inbox_tasks_cnt === 0) {
    return 10;
  }

  const pct = Math.floor(
    (bigPlanStats.completed_inbox_tasks_cnt /
      bigPlanStats.all_inbox_tasks_cnt) *
      100,
  );

  if (pct < 10) {
    return 10;
  } else if (pct > 95) {
    return 95;
  }

  return pct;
}

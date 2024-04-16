import type { BigPlan } from "webapi-client";
import { compareADate } from "./adate";
import { compareBigPlanStatus } from "./big-plan-status";

export function sortBigPlansNaturally(
  bigPlans: Array<BigPlan>
): Array<BigPlan> {
  return [...bigPlans].sort((e1, e2) => {
    return (
      compareADate(e1.actionable_date, e2.actionable_date) ||
      compareADate(e1.due_date, e2.due_date) ||
      compareBigPlanStatus(e1.status, e2.status)
    );
  });
}

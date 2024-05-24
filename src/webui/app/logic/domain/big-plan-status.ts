import { BigPlan, BigPlanStatus } from "@jupiter/webapi-client";

export function bigPlanStatusName(status: BigPlanStatus): string {
  switch (status) {
    case BigPlanStatus.NOT_STARTED:
      return "Not Started";
    case BigPlanStatus.ACCEPTED:
      return "Accepted";
    case BigPlanStatus.IN_PROGRESS:
      return "In Progress";
    case BigPlanStatus.BLOCKED:
      return "Blocked";
    case BigPlanStatus.NOT_DONE:
      return "Not Done";
    case BigPlanStatus.DONE:
      return "Done";
  }
}

export function bigPlanStatusIcon(status: BigPlanStatus): string {
  switch (status) {
    case BigPlanStatus.NOT_STARTED:
      return "📥";
    case BigPlanStatus.ACCEPTED:
      return "🔧";
    case BigPlanStatus.IN_PROGRESS:
      return "🚧";
    case BigPlanStatus.BLOCKED:
      return "🚧";
    case BigPlanStatus.NOT_DONE:
      return "⛔";
    case BigPlanStatus.DONE:
      return "✅";
  }
}

const BIG_PLAN_STATUS_MAP = {
  [BigPlanStatus.NOT_STARTED]: 0,
  [BigPlanStatus.ACCEPTED]: 1,
  [BigPlanStatus.IN_PROGRESS]: 2,
  [BigPlanStatus.BLOCKED]: 3,
  [BigPlanStatus.NOT_DONE]: 4,
  [BigPlanStatus.DONE]: 5,
};

export function compareBigPlanStatus(
  status1: BigPlanStatus,
  status2: BigPlanStatus
): number {
  return BIG_PLAN_STATUS_MAP[status1] - BIG_PLAN_STATUS_MAP[status2];
}

export function isCompleted(status: BigPlanStatus): boolean {
  return status === BigPlanStatus.DONE || status === BigPlanStatus.NOT_DONE;
}

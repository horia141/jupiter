import {
  TimePlanActivityTarget,
  type BigPlan,
  type InboxTask,
  type TimePlanActivity,
} from "@jupiter/webapi-client";
import { compareTimePlanActivityFeasability } from "./time-plan-activity-feasability";
import { compareTimePlanActivityKind } from "./time-plan-activity-kind";

const TIME_PLAN_ACTIVITY_TARGET_MAP = {
  [TimePlanActivityTarget.BIG_PLAN]: 0,
  [TimePlanActivityTarget.INBOX_TASK]: 1,
};

export function filterActivitiesByTargetStatus(
  timePlanActivities: TimePlanActivity[],
  targetInboxTasks: Map<string, InboxTask>,
  targetBigPlans: Map<string, BigPlan>,
  activityDoneness: Record<string, boolean>
): TimePlanActivity[] {
  return timePlanActivities.filter((activity) => {
    if (activityDoneness[activity.ref_id]) {
      return false;
    }

    switch (activity.target) {
      case TimePlanActivityTarget.INBOX_TASK:
        const inboxTask = targetInboxTasks.get(activity.target_ref_id)!;
        return !inboxTask.archived;
      case TimePlanActivityTarget.BIG_PLAN:
        const bigPlan = targetBigPlans.get(activity.target_ref_id)!;
        return !bigPlan.archived;
    }

    throw new Error("This should not happen");
  });
}

export function sortTimePlanActivitiesNaturally(
  timePlanActivities: TimePlanActivity[],
  targetInboxTasks: Map<string, InboxTask>,
  targetBigPlans: Map<string, BigPlan>
): TimePlanActivity[] {
  return [...timePlanActivities].sort((j1, j2) => {
    const j1Parent =
      j1.target === TimePlanActivityTarget.BIG_PLAN
        ? j1.target_ref_id
        : targetInboxTasks.get(j1.target_ref_id)!.big_plan_ref_id;
    const j2Parent =
      j2.target === TimePlanActivityTarget.BIG_PLAN
        ? j2.target_ref_id
        : targetInboxTasks.get(j2.target_ref_id)!.big_plan_ref_id;

    if (j1Parent !== j2Parent) {
      if (j1Parent === undefined || j1Parent === null) {
        return 1;
      }
      if (j2Parent === undefined || j2Parent === null) {
        return -1;
      }

      return j1Parent.localeCompare(j2Parent);
    }

    if (j1.target !== j2.target) {
      return (
        TIME_PLAN_ACTIVITY_TARGET_MAP[j1.target] -
        TIME_PLAN_ACTIVITY_TARGET_MAP[j2.target]
      );
    }

    if (j2.archived && !j1.archived) {
      return -1;
    }

    if (j1.archived && !j2.archived) {
      return 1;
    }

    return (
      compareTimePlanActivityFeasability(j1.feasability, j2.feasability) ||
      compareTimePlanActivityKind(j1.kind, j2.kind)
    );
  });
}

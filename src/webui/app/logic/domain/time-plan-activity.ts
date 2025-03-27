import type {
  BigPlan,
  InboxTask,
  TimePlanActivity,
  TimePlanActivityFeasability,
} from "@jupiter/webapi-client";
import {
  InboxTaskSource,
  TimePlanActivityTarget,
} from "@jupiter/webapi-client";
import { compareTimePlanActivityFeasability } from "./time-plan-activity-feasability";
import { compareTimePlanActivityKind } from "./time-plan-activity-kind";

const TIME_PLAN_ACTIVITY_TARGET_MAP = {
  [TimePlanActivityTarget.BIG_PLAN]: 0,
  [TimePlanActivityTarget.INBOX_TASK]: 1,
};

export function filterActivityByFeasabilityWithParents(
  timePlanActivities: TimePlanActivity[],
  activitiesByBigPlanRefId: Map<string, TimePlanActivity>,
  targetInboxTasks: Map<string, InboxTask>,
  targetBigPlans: Map<string, BigPlan>,
  feasability: TimePlanActivityFeasability,
): TimePlanActivity[] {
  return timePlanActivities.filter((a) => {
    if (a.target === TimePlanActivityTarget.BIG_PLAN) {
      return a.feasability === feasability;
    } else {
      const inboxTask = targetInboxTasks.get(a.target_ref_id)!;
      if (inboxTask.source !== InboxTaskSource.BIG_PLAN) {
        return a.feasability === feasability;
      }

      const bigPlan = targetBigPlans.get(inboxTask.source_entity_ref_id!)!;
      const bigPlanActivity = activitiesByBigPlanRefId.get(bigPlan.ref_id)!;

      return bigPlanActivity.feasability === feasability;
    }
  });
}

export function filterActivitiesByTargetStatus(
  timePlanActivities: TimePlanActivity[],
  targetInboxTasks: Map<string, InboxTask>,
  targetBigPlans: Map<string, BigPlan>,
  activityDoneness: Record<string, boolean>,
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
  targetBigPlans: Map<string, BigPlan>,
): TimePlanActivity[] {
  return [...timePlanActivities].sort((j1, j2) => {
    const j1Parent =
      j1.target === TimePlanActivityTarget.BIG_PLAN
        ? j1.target_ref_id
        : targetInboxTasks.get(j1.target_ref_id)!.source ===
            InboxTaskSource.BIG_PLAN
          ? targetInboxTasks.get(j1.target_ref_id)!.source_entity_ref_id
          : undefined;
    const j2Parent =
      j2.target === TimePlanActivityTarget.BIG_PLAN
        ? j2.target_ref_id
        : targetInboxTasks.get(j2.target_ref_id)!.source ===
            InboxTaskSource.BIG_PLAN
          ? targetInboxTasks.get(j2.target_ref_id)!.source_entity_ref_id
          : undefined;

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

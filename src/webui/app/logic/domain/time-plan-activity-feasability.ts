import { TimePlanActivityFeasability } from "@jupiter/webapi-client";

export function timePlanActivityFeasabilityName(
  feasability: TimePlanActivityFeasability
): string {
  switch (feasability) {
    case TimePlanActivityFeasability.MUST_DO:
      return "Must Do";
    case TimePlanActivityFeasability.NICE_TO_HAVE:
      return "Nice To Have";
    case TimePlanActivityFeasability.STRETCH:
      return "Stretch";
  }
}

const TIME_PLAN_ACTIVITY_FEASABILITY_MAP = {
  [TimePlanActivityFeasability.MUST_DO]: 0,
  [TimePlanActivityFeasability.NICE_TO_HAVE]: 1,
  [TimePlanActivityFeasability.STRETCH]: 2,
};

export function compareTimePlanActivityFeasability(
  feasability1: TimePlanActivityFeasability,
  feasability2: TimePlanActivityFeasability
): number {
  return (
    TIME_PLAN_ACTIVITY_FEASABILITY_MAP[feasability1] -
    TIME_PLAN_ACTIVITY_FEASABILITY_MAP[feasability2]
  );
}

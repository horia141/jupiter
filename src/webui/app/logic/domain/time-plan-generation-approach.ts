import { TimePlanGenerationApproach } from "@jupiter/webapi-client";

export function approachName(
  approach: TimePlanGenerationApproach,
  short: boolean,
): string {
  switch (approach) {
    case TimePlanGenerationApproach.BOTH_PLAN_AND_TASK:
      return short ? "Both" : "Both Plan and Task";
    case TimePlanGenerationApproach.ONLY_PLAN:
      return short ? "Plan" : "Only Plan";
    case TimePlanGenerationApproach.NONE:
      return short ? "None" : "None";
  }
}

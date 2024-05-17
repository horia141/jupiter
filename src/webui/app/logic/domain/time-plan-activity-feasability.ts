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

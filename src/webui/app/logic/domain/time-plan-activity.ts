import { compareTimePlanActivityFeasability } from "./time-plan-activity-feasability";
import { compareTimePlanActivityKind } from "./time-plan-activity-kind";

export function sortTimePlanActivitiesNaturally(timePlanActivities: TimePlanActivity[]): TimePlanActivity[] {
    return [...timePlanActivities].sort((j1, j2) => {
        if (j2.archived && !j1.archived) {
          return -1;
        }
    
        if (j1.archived && !j2.archived) {
          return 1;
        }

        return (
            compareTimePlanActivityFeasability(j1.feasability, 2.feasability) ||
            compareTimePlanActivityKind(j1.kind, j2.kind)
        );
      });
}
import type { TimePlan } from "@jupiter/webapi-client";
import type { TopLevelInfo } from "~/top-level-context";
import { EntityStack } from "./infra/entity-stack";
import { TimePlanCard } from "./time-plan-card";

interface TimePlanStackProps {
  topLevelInfo: TopLevelInfo;
  timePlans: Array<TimePlan>;
  allowSwipe?: boolean;
  allowMarkNotDone?: boolean;
  relativeToTimePlan?: TimePlan;
  onMarkNotDone?: (timePlan: TimePlan) => void;
}

export function TimePlanStack(props: TimePlanStackProps) {
  return (
    <EntityStack>
      {props.timePlans.map((timePlan) => (
        <TimePlanCard
          key={`time-plan-${timePlan.ref_id}`}
          topLevelInfo={props.topLevelInfo}
          timePlan={timePlan}
          allowSwipe={props.allowSwipe}
          allowMarkNotDone={props.allowMarkNotDone}
          onMarkNotDone={props.onMarkNotDone}
          relativeToTimePlan={props.relativeToTimePlan}
        />
      ))}
    </EntityStack>
  );
}

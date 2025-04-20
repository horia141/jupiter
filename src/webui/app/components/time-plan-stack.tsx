import type { TimePlan } from "@jupiter/webapi-client";

import type { TopLevelInfo } from "~/top-level-context";

import { EntityStack2 } from "./infra/entity-stack";
import { StandardDivider } from "./standard-divider";
import { TimePlanCard } from "./time-plan-card";

interface TimePlanStackProps {
  label?: string;
  topLevelInfo: TopLevelInfo;
  timePlans: Array<TimePlan>;
  allowSwipe?: boolean;
  allowMarkNotDone?: boolean;
  relativeToTimePlan?: TimePlan;
  onMarkNotDone?: (timePlan: TimePlan) => void;
}

export function TimePlanStack(props: TimePlanStackProps) {
  return (
    <EntityStack2>
      {props.label && <StandardDivider title={props.label} size="large" />}

      {props.timePlans.map((timePlan) => (
        <TimePlanCard
          key={`time-plan-${timePlan.ref_id}`}
          topLevelInfo={props.topLevelInfo}
          timePlan={timePlan}
          showOptions={{
            showSource: true,
            showPeriod: true,
          }}
          allowSwipe={props.allowSwipe}
          allowMarkNotDone={props.allowMarkNotDone}
          onMarkNotDone={props.onMarkNotDone}
          relativeToTimePlan={props.relativeToTimePlan}
        />
      ))}
    </EntityStack2>
  );
}

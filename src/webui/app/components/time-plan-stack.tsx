import type { TimePlan } from "@jupiter/webapi-client";
import type { TopLevelInfo } from "~/top-level-context";
import { EntityNameComponent } from "./entity-name";
import { EntityCard, EntityLink } from "./infra/entity-card";
import { EntityStack } from "./infra/entity-stack";
import { PeriodTag } from "./period-tag";
import { TimePlanSourceTag } from "./time-plan-source-tag";
import { TimePlanCard } from "./time-plan-card";

interface TimePlanStackProps {
  topLevelInfo: TopLevelInfo;
  timePlans: Array<TimePlan>;
  allowSwipe?: boolean;
  allowMarkNotDone?: boolean;
  onMarkNotDone?: (timePlan: TimePlan) => void;
}

export function TimePlanStack(props: TimePlanStackProps) {
  return (
    <EntityStack>
      {props.timePlans.map((timePlan) => (
        <TimePlanCard
          topLevelInfo={props.topLevelInfo}
          timePlan={timePlan}
          allowSwipe={props.allowSwipe}
          allowMarkNotDone={props.allowMarkNotDone}
          onMarkNotDone={props.onMarkNotDone} />
      ))}
    </EntityStack>
  );
}

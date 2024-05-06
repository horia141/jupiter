import type { TimePlan } from "@jupiter/webapi-client";
import type { TopLevelInfo } from "~/top-level-context";
import { EntityNameComponent } from "./entity-name";
import { EntityCard, EntityLink } from "./infra/entity-card";
import { EntityStack } from "./infra/entity-stack";
import { PeriodTag } from "./period-tag";
import { TimePlanSourceTag } from "./time-plan-source-tag";

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
        <EntityCard
          key={`time-plan-${timePlan.ref_id}`}
          entityId={`time-plan-${timePlan.ref_id}`}
          allowSwipe={props.allowSwipe}
          allowMarkNotDone={props.allowMarkNotDone}
          onMarkNotDone={() =>
            props.onMarkNotDone && props.onMarkNotDone(timePlan)
          }
        >
          <EntityLink to={`/workspace/time-plans/${timePlan.ref_id}`}>
            <EntityNameComponent name={timePlan.name} />
            <TimePlanSourceTag source={timePlan.source} />
            <PeriodTag period={timePlan.period} />
            TODO: Something around activities here!
          </EntityLink>
        </EntityCard>
      ))}
    </EntityStack>
  );
}

import type { TimePlan } from "@jupiter/webapi-client";
import type { TopLevelInfo } from "~/top-level-context";

import { EntityNameComponent } from "./entity-name";
import { EntityCard, EntityLink } from "./infra/entity-card";
import { PeriodTag } from "./period-tag";
import { TimePlanSourceTag } from "./time-plan-source-tag";

interface TimePlanCardProps {
  topLevelInfo: TopLevelInfo;
  timePlan: TimePlan;
  relativeToTimePlan?: TimePlan;
  allowSwipe?: boolean;
  allowMarkNotDone?: boolean;
  onMarkNotDone?: (timePlan: TimePlan) => void;
}

export function TimePlanCard(props: TimePlanCardProps) {
  const timePlan = props.timePlan;
  const link =
    props.relativeToTimePlan !== undefined
      ? `/app/workspace/time-plans/${props.relativeToTimePlan.ref_id}/add-from-current-time-plans/${timePlan.ref_id}`
      : `/app/workspace/time-plans/${timePlan.ref_id}`;
  return (
    <EntityCard
      entityId={`time-plan-${timePlan.ref_id}`}
      allowSwipe={props.allowSwipe}
      allowMarkNotDone={props.allowMarkNotDone}
      onMarkNotDone={() => props.onMarkNotDone && props.onMarkNotDone(timePlan)}
    >
      <EntityLink to={link}>
        <EntityNameComponent name={timePlan.name} />
        <TimePlanSourceTag source={timePlan.source} />
        <PeriodTag period={timePlan.period} />
      </EntityLink>
    </EntityCard>
  );
}

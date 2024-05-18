import type { TimePlan } from "@jupiter/webapi-client";
import type { TopLevelInfo } from "~/top-level-context";
import { EntityNameComponent } from "./entity-name";
import { EntityCard, EntityLink } from "./infra/entity-card";
import { EntityStack } from "./infra/entity-stack";
import { PeriodTag } from "./period-tag";
import { TimePlanSourceTag } from "./time-plan-source-tag";

interface TimePlanCardProps {
    topLevelInfo: TopLevelInfo;
    timePlan: TimePlan;
    allowSwipe?: boolean;
    allowMarkNotDone?: boolean;
    onMarkNotDone?: (timePlan: TimePlan) => void;
}

export function TimePlanCard(props: TimePlanCardProps) {
    return (
        <EntityCard
            entityId={`time-plan-${props.timePlan.ref_id}`}
            allowSwipe={props.allowSwipe}
            allowMarkNotDone={props.allowMarkNotDone}
            onMarkNotDone={() =>
                props.onMarkNotDone && props.onMarkNotDone(timePlan)
              }>
            <EntityLink to={`/workspace/time-plans/${timePlan.ref_id}`}>
                <EntityNameComponent name={timePlan.name} />
                <TimePlanSourceTag source={timePlan.source} />
                <PeriodTag period={timePlan.period} />
                TODO: Something around activities here!
            </EntityLink>
        </EntityCard>
    );
}
import type { BigPlan } from "@jupiter/webapi-client";

import type { BigPlanParent } from "~/logic/domain/big-plan";
import type { TopLevelInfo } from "~/top-level-context";

import type { BigPlanShowOptions } from "./big-plan-card";
import { BigPlanCard } from "./big-plan-card";
import { EntityStack } from "./infra/entity-stack";
import { StandardDivider } from "./standard-divider";

interface BigPlanStackProps {
  topLevelInfo: TopLevelInfo;
  label?: string;
  bigPlans: BigPlan[];
  entriesByRefId?: Map<string, BigPlanParent>;
  selectedPredicate?: (it: BigPlan) => boolean;
  compact?: boolean;
  showOptions: BigPlanShowOptions;
  allowSelect?: boolean;
  allowSwipe?: boolean;
  onClick?: (it: BigPlan) => void;
  onCardMarkDone?: (it: BigPlan) => void;
  onCardMarkNotDone?: (it: BigPlan) => void;
}

export function BigPlanStack(props: BigPlanStackProps) {
  return (
    <EntityStack>
      {props.label && <StandardDivider title={props.label} size="large" />}

      {props.bigPlans.map((entry) => {
        return (
          <BigPlanCard
            key={`big-plan-${entry.ref_id}`}
            topLevelInfo={props.topLevelInfo}
            allowSwipe={props.allowSwipe}
            compact={props.compact}
            allowSelect={props.allowSelect}
            bigPlan={entry}
            selected={props.selectedPredicate?.(entry)}
            showOptions={props.showOptions}
            parent={props.entriesByRefId?.get(entry.ref_id)}
            onClick={
              props.onClick
                ? () => props.onClick && props.onClick(entry)
                : undefined
            }
            onMarkDone={
              props.onCardMarkDone
                ? () => props.onCardMarkDone && props.onCardMarkDone(entry)
                : undefined
            }
            onMarkNotDone={
              props.onCardMarkNotDone
                ? () =>
                    props.onCardMarkNotDone && props.onCardMarkNotDone(entry)
                : undefined
            }
          />
        );
      })}
    </EntityStack>
  );
}

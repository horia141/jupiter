import type {
  BigPlan,
  BigPlanMilestone,
  BigPlanStats,
} from "@jupiter/webapi-client";
import { Stack } from "@mui/material";

import type { BigPlanParent } from "~/logic/domain/big-plan";
import type { TopLevelInfo } from "~/top-level-context";
import type { BigPlanShowOptions } from "~/components/domain/concept/big-plan/big-plan-card";
import { BigPlanCard } from "~/components/domain/concept/big-plan/big-plan-card";
import { StandardDivider } from "~/components/infra/standard-divider";

interface BigPlanStackProps {
  topLevelInfo: TopLevelInfo;
  label?: string;
  bigPlans: BigPlan[];
  bigPlanMilestonesByRefId?: Map<string, BigPlanMilestone[]>;
  bigPlanStatsByRefId?: Map<string, BigPlanStats>;
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
    <Stack spacing={0.5}>
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
            bigPlanMilestones={props.bigPlanMilestonesByRefId?.get(
              entry.ref_id,
            )}
            bigPlanStats={props.bigPlanStatsByRefId?.get(entry.ref_id)}
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
    </Stack>
  );
}

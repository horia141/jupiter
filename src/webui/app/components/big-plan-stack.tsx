import type { BigPlan } from "@jupiter/webapi-client";
import { Divider, Typography } from "@mui/material";
import type { BigPlanParent } from "~/logic/domain/big-plan";
import type { TopLevelInfo } from "~/top-level-context";
import { BigPlanCard } from "./big-plan-card";
import { EntityStack } from "./infra/entity-stack";

interface BigPlanStackProps {
  topLevelInfo: TopLevelInfo;
  showLabel?: boolean;
  label?: string;
  bigPlans: BigPlan[];
  entriesByRefId?: Map<string, BigPlanParent>;
  onCardMarkDone?: (it: BigPlan) => void;
  onCardMarkNotDone?: (it: BigPlan) => void;
}

export function BigPlanStack(props: BigPlanStackProps) {
  return (
    <EntityStack>
      {props.showLabel && (
        <Divider style={{ paddingTop: "0.5rem" }}>
          <Typography variant="h6">{props.label}</Typography>
        </Divider>
      )}

      {props.bigPlans.map((entry) => {
        return (
          <BigPlanCard
            key={`big-plan-${entry.ref_id}`}
            topLevelInfo={props.topLevelInfo}
            allowSwipe
            bigPlan={entry}
            showOptions={{
              showStatus: true,
              showParent: true,
              showActionableDate: true,
              showDueDate: true,
              showHandleMarkDone: true,
              showHandleMarkNotDone: true,
            }}
            parent={props.entriesByRefId?.get(entry.ref_id)}
            onMarkDone={() =>
              props.onCardMarkDone && props.onCardMarkDone(entry)
            }
            onMarkNotDone={() =>
              props.onCardMarkNotDone && props.onCardMarkNotDone(entry)
            }
          />
        );
      })}
    </EntityStack>
  );
}

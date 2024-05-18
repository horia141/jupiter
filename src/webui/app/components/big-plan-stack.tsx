import { Divider, Typography } from "@mui/material";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import type { TopLevelInfo } from "~/top-level-context";
import { ADateTag } from "./adate-tag";
import { BigPlanStatusTag } from "./big-plan-status-tag";
import { EntityNameComponent } from "./entity-name";
import { EntityCard, EntityLink } from "./infra/entity-card";
import { EntityStack } from "./infra/entity-stack";
import { ProjectTag } from "./project-tag";
import { BigPlan, BigPlanFindResultEntry, Project, WorkspaceFeature } from "@jupiter/webapi-client";
import { BigPlanCard } from "./big-plan-card";

interface BigPlanStackProps {
  topLevelInfo: TopLevelInfo;
  showLabel?: boolean;
  label?: string;
  bigPlans: BigPlan[];
  entriesByRefId?: Map<string, BigPlanFindResultEntry>;
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

      {props.bigPlans.map((entry) => (
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
            showHandleMarkNotDone: true
          }}
          parent={foogazi}
          onMarkDone={() => props.onCardMarkDone && props.onCardMarkDone(entry)}
          onMarkNotDone={() =>
            props.onCardMarkNotDone && props.onCardMarkNotDone(entry)
          }
        />
      ))}
    </EntityStack>
  );
}

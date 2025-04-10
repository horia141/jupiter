import type { BigPlan, Project } from "@jupiter/webapi-client";
import { WorkspaceFeature } from "@jupiter/webapi-client";
import { Divider } from "@mui/material";

import type { BigPlanParent } from "~/logic/domain/big-plan";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import type { TopLevelInfo } from "~/top-level-context";

import { ADateTag } from "./adate-tag";
import { BigPlanStatusTag } from "./big-plan-status-tag";
import { EntityNameComponent } from "./entity-name";
import { EntityCard, EntityLink } from "./infra/entity-card";
import { ProjectTag } from "./project-tag";

export interface BigPlanShowOptions {
  showStatus?: boolean;
  showParent?: boolean;
  showActionableDate?: boolean;
  showDueDate?: boolean;
  showHandleMarkDone?: boolean;
  showHandleMarkNotDone?: boolean;
}

export interface BigPlanCardProps {
  topLevelInfo: TopLevelInfo;
  compact?: boolean;
  allowSwipe?: boolean;
  allowSelect?: boolean;
  selected?: boolean;
  showOptions: BigPlanShowOptions;
  bigPlan: BigPlan;
  parent?: BigPlanParent;
  onClick?: (it: BigPlan) => void;
  onMarkDone?: (it: BigPlan) => void;
  onMarkNotDone?: (it: BigPlan) => void;
}

export function BigPlanCard(props: BigPlanCardProps) {
  return (
    <EntityCard
      entityId={`big-plan-${props.bigPlan.ref_id}`}
      allowSwipe={props.allowSwipe}
      allowSelect={props.allowSelect}
      selected={props.selected}
      allowMarkDone={props.showOptions.showHandleMarkDone}
      allowMarkNotDone={props.showOptions.showHandleMarkNotDone}
      onClick={
        props.onClick
          ? () => props.onClick && props.onClick(props.bigPlan)
          : undefined
      }
      markButtonsStyle="column"
      onMarkDone={
        props.onMarkDone
          ? () => props.onMarkDone && props.onMarkDone(props.bigPlan)
          : undefined
      }
      onMarkNotDone={
        props.onMarkNotDone
          ? () => props.onMarkNotDone && props.onMarkNotDone(props.bigPlan)
          : undefined
      }
    >
      <EntityLink
        to={`/app/workspace/big-plans/${props.bigPlan.ref_id}`}
        block={props.onClick !== undefined}
      >
        <EntityNameComponent
          compact={props.compact}
          name={props.bigPlan.name}
        />
        <Divider />
        {props.showOptions.showStatus && (
          <BigPlanStatusTag status={props.bigPlan.status} />
        )}
        {props.showOptions.showParent &&
          isWorkspaceFeatureAvailable(
            props.topLevelInfo.workspace,
            WorkspaceFeature.PROJECTS,
          ) &&
          props.parent && (
            <ProjectTag project={props.parent.project as Project} />
          )}

        {props.showOptions.showActionableDate &&
          props.bigPlan.actionable_date && (
            <ADateTag
              label="Actionable Date"
              date={props.bigPlan.actionable_date}
            />
          )}
        {props.showOptions.showDueDate && props.bigPlan.due_date && (
          <ADateTag label="Due Date" date={props.bigPlan.due_date} />
        )}
      </EntityLink>
    </EntityCard>
  );
}

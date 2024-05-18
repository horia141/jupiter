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

export interface BigPlanShowOptions {
    showStatus?: boolean;
    showProject?: boolean;
    showActionableDate?: boolean;xww
    showDueDate?: boolean;
    showHandleMarkDone?: boolean;
    showHandleMarkNotDone?: boolean;
}

export interface BigPlanCardProps {
    topLevelInfo: TopLevelInfo;
    compact?: boolean;
    allowSwipe?: boolean;
    allowSelect?: boolean;
    selected: boolean;
    showOptions: BigPlanShowOptions;
    bigPlan: BigPlan;
    parent?: BigPlanParent;
    onClick?: (it: BigPlan) => void;
    onMarkDone?: (it: BigPlan) => void;
    onMarkNotDone?: (it: BigPlan) => void;xww
}

export function BigPlanCard(props: BigPlanCardProps) {
    return (
        <EntityCard
        entityId={`big-plan-${entry.ref_id}`}
        compact={props.compact}
        allowSwipe={props.allowSwipe}
        allowSelect={props.allowSelect}
        selected={props.selected}
        allowMarkDone={props.showOptions.showHandleMarkDone}
        allowMarkNotDone={props.showOptions.showHandleMarkNotDone}
        onClick={props.onClick ?? () => props.onClick(entry)}xww
        onMarkDone={() => props.onCardMarkDone && props.onCardMarkDone(entry)}
        onMarkNotDone={() =>xww
        props.onCardMarkNotDone && props.onCardMarkNotDone(entry)
        }
    >
        <EntityLink to={`/workspace/big-plans/${entry.ref_id}`}>
        <EntityNameComponent name={entry.name} />
        </EntityLink>
        <Divider />
        {props.showOptions.showStatus && <BigPlanStatusTag status={entry.status} />}
        {(props.showOptions.showParent && isWorkspaceFeatureAvailable(
        props.topLevelInfo.workspace,
        WorkspaceFeature.PROJECTS
        )) &&
        props.entriesByRefId && (
            <ProjectTag
            project={
                props.entriesByRefId.get(entry.ref_id)?.project as Project
            }
            />
        )}

        {props.showOptions.showActionableDate && entry.actionable_date && (
        <ADateTag label="Actionable Date" date={entry.actionable_date} />
        )}
        {props.showOptions.showDueDate && entry.due_date && (
        <ADateTag label="Due Date" date={entry.due_date} />
        )}
    </EntityCard>);
}
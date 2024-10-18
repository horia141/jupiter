import type {
  BigPlan,
  InboxTask,
  TimePlan,
  TimePlanActivity,
} from "@jupiter/webapi-client";
import {
  BigPlanStatus,
  InboxTaskStatus,
  TimePlanActivityTarget,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import { Typography } from "@mui/material";
import { BigPlanStatusTag } from "~/components/big-plan-status-tag";
import { InboxTaskStatusTag } from "~/components/inbox-task-status-tag";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { TimePlanActivityFeasabilityTag } from "~/components/time-plan-activity-feasability-tag";
import { TimePlanActivityKindTag } from "~/components/time-plan-activity-kind-tag";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import type { TopLevelInfo } from "~/top-level-context";
import { ADateTag } from "./adate-tag";

interface TimePlanActivityCardProps {
  topLevelInfo: TopLevelInfo;
  timePlan: TimePlan;
  activity: TimePlanActivity;
  inboxTasksByRefId: Map<string, InboxTask>;
  bigPlansByRefId: Map<string, BigPlan>;
  activityDoneness: Record<string, boolean>;
  allowSelect?: boolean;
  selected?: boolean;
  indent?: number;
  onClick?: (activity: TimePlanActivity) => void;
}

export function TimePlanActivityCard(props: TimePlanActivityCardProps) {
  if (props.activity.target === TimePlanActivityTarget.INBOX_TASK) {
    const inboxTask = props.inboxTasksByRefId.get(props.activity.target_ref_id);

    return (
      <EntityCard
        entityId={`time-plan-activity-${props.timePlan.ref_id}`}
        allowSelect={props.allowSelect}
        selected={props.selected}
        indent={props.indent}
        onClick={
          props.onClick
            ? () => props.onClick && props.onClick(props.activity)
            : undefined
        }
        backgroundHint={
          props.activityDoneness[props.activity.ref_id]
            ? inboxTask?.status === InboxTaskStatus.NOT_DONE
              ? "failure"
              : "success"
            : "neutral"
        }
      >
        <EntityLink
          to={`/workspace/time-plans/${props.timePlan.ref_id}/${props.activity.ref_id}`}
          block={props.onClick !== undefined}
        >
          <Typography
            sx={{
              fontWeight: inboxTask
                ? props.activityDoneness[props.activity.ref_id]
                  ? "bold"
                  : "normal"
                : "lighter",
            }}
          >
            {inboxTask ? inboxTask.name : "Archived Task"}
          </Typography>
          {inboxTask && <InboxTaskStatusTag status={inboxTask.status} />}
          {inboxTask?.due_date && (
            <ADateTag label="Due At" date={inboxTask.due_date} />
          )}
          <TimePlanActivityKindTag kind={props.activity.kind} />
          <TimePlanActivityFeasabilityTag
            feasability={props.activity.feasability}
          />
        </EntityLink>
      </EntityCard>
    );
  } else if (
    isWorkspaceFeatureAvailable(
      props.topLevelInfo.workspace,
      WorkspaceFeature.BIG_PLANS
    )
  ) {
    const bigPlan = props.bigPlansByRefId.get(props.activity.target_ref_id);
    return (
      <EntityCard
        entityId={`time-plan-activity-${props.timePlan.ref_id}`}
        allowSelect={props.allowSelect}
        selected={props.selected}
        onClick={
          props.onClick
            ? () => props.onClick && props.onClick(props.activity)
            : undefined
        }
        backgroundHint={
          props.activityDoneness[props.activity.ref_id]
            ? bigPlan?.status === BigPlanStatus.NOT_DONE
              ? "failure"
              : "success"
            : "neutral"
        }
      >
        <EntityLink
          to={`/workspace/time-plans/${props.timePlan.ref_id}/${props.activity.ref_id}`}
          block={props.onClick !== undefined}
        >
          <Typography
            sx={{
              fontWeight: bigPlan
                ? props.activityDoneness[props.activity.ref_id]
                  ? "bold"
                  : "normal"
                : "lighter",
            }}
          >
            {bigPlan ? bigPlan.name : "Archived Big Plan"}
          </Typography>
          {bigPlan && <BigPlanStatusTag status={bigPlan.status} />}
          {bigPlan?.due_date && (
            <ADateTag label="Due At" date={bigPlan.due_date} />
          )}
          <TimePlanActivityKindTag kind={props.activity.kind} />
          <TimePlanActivityFeasabilityTag
            feasability={props.activity.feasability}
          />
        </EntityLink>
      </EntityCard>
    );
  } else {
    return <></>;
  }
}

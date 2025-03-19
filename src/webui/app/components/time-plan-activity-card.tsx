import type {
  BigPlan,
  InboxTask,
  TimeEventInDayBlock,
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
import { TimePlanTag } from "./time-plan-tag";

interface TimePlanActivityCardProps {
  topLevelInfo: TopLevelInfo;
  activity: TimePlanActivity;
  timePlansByRefId: Map<string, TimePlan>;
  inboxTasksByRefId: Map<string, InboxTask>;
  bigPlansByRefId: Map<string, BigPlan>;
  activityDoneness: Record<string, boolean>;
  timeEventsByRefId: Map<string, Array<TimeEventInDayBlock>>;
  fullInfo: boolean;
  allowSelect?: boolean;
  selected?: boolean;
  indent?: number;
  onClick?: (activity: TimePlanActivity) => void;
}

export function TimePlanActivityCard(props: TimePlanActivityCardProps) {
  const timePlan = props.timePlansByRefId.get(
    props.activity.time_plan_ref_id.toString()
  );

  if (props.activity.target === TimePlanActivityTarget.INBOX_TASK) {
    const inboxTask = props.inboxTasksByRefId.get(
      props.activity.target_ref_id
    )!;
    const timeEvents =
      props.timeEventsByRefId.get(`it:${inboxTask.ref_id}`) ?? [];

    return (
      <EntityCard
        entityId={`time-plan-activity-${props.activity.ref_id}`}
        showAsArchived={props.activity.archived}
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
          to={`/app/workspace/time-plans/${props.activity.time_plan_ref_id}/${props.activity.ref_id}`}
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
          {props.fullInfo && (
            <>
              {inboxTask && <InboxTaskStatusTag status={inboxTask.status} />}
              {inboxTask?.due_date && (
                <ADateTag label="Due At" date={inboxTask.due_date} />
              )}

              {timeEvents.length > 0 && (
                <>
                  📅 {timeEvents.length} scheduled event
                  {timeEvents.length > 1 ? "s" : ""}
                </>
              )}
            </>
          )}

          <TimePlanActivityKindTag kind={props.activity.kind} />
          <TimePlanActivityFeasabilityTag
            feasability={props.activity.feasability}
          />

          {timePlan && <TimePlanTag timePlan={timePlan} />}
        </EntityLink>
      </EntityCard>
    );
  } else if (
    isWorkspaceFeatureAvailable(
      props.topLevelInfo.workspace,
      WorkspaceFeature.BIG_PLANS
    )
  ) {
    const bigPlan = props.bigPlansByRefId.get(props.activity.target_ref_id)!;
    const timeEvents =
      props.timeEventsByRefId.get(`bp:${bigPlan.ref_id}`) ?? [];
    return (
      <EntityCard
        entityId={`time-plan-activity-${props.activity.ref_id}`}
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
          to={`/app/workspace/time-plans/${props.activity.time_plan_ref_id}/${props.activity.ref_id}`}
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

          {props.fullInfo && (
            <>
              {bigPlan && <BigPlanStatusTag status={bigPlan.status} />}
              {bigPlan?.due_date && (
                <ADateTag label="Due At" date={bigPlan.due_date} />
              )}

              {timeEvents.length > 0 && (
                <>
                  📅 {timeEvents.length} scheduled event
                  {timeEvents.length > 1 ? "s" : ""}
                </>
              )}
            </>
          )}

          <TimePlanActivityKindTag kind={props.activity.kind} />
          <TimePlanActivityFeasabilityTag
            feasability={props.activity.feasability}
          />

          {timePlan && <TimePlanTag timePlan={timePlan} />}
        </EntityLink>
      </EntityCard>
    );
  } else {
    return <></>;
  }
}

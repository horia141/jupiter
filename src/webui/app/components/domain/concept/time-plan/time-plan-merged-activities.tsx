import { useContext } from "react";
import type {
  TimePlanActivity,
  TimePlanActivityKind,
  TimePlanActivityFeasability,
  TimePlanActivityDoneness,
  InboxTask,
  BigPlan,
  TimeEventInDayBlock,
} from "@jupiter/webapi-client";

import { StandardDivider } from "~/components/infra/standard-divider";
import { TimePlanActivityList } from "~/components/domain/concept/time-plan/time-plan-activity-list";
import { TopLevelInfoContext } from "~/top-level-context";

interface TimePlanMergedActivitiesProps {
  mustDoActivities: TimePlanActivity[];
  niceToHaveActivities: TimePlanActivity[];
  stretchActivities: TimePlanActivity[];
  targetInboxTasksByRefId: Map<string, InboxTask>;
  targetBigPlansByRefId: Map<string, BigPlan>;
  activityDoneness: Record<string, TimePlanActivityDoneness>;
  timeEventsByRefId: Map<string, TimeEventInDayBlock[]>;
  selectedKinds: TimePlanActivityKind[];
  selectedFeasabilities: TimePlanActivityFeasability[];
  selectedDoneness: boolean[];
}

export function TimePlanMergedActivities(props: TimePlanMergedActivitiesProps) {
  const topLevelInfo = useContext(TopLevelInfoContext);

  return (
    <>
      {props.mustDoActivities.length > 0 && (
        <>
          <StandardDivider title="Must Do" size="large" />

          <TimePlanActivityList
            topLevelInfo={topLevelInfo}
            activities={props.mustDoActivities}
            inboxTasksByRefId={props.targetInboxTasksByRefId}
            timePlansByRefId={new Map()}
            bigPlansByRefId={props.targetBigPlansByRefId}
            activityDoneness={props.activityDoneness}
            fullInfo
            filterKind={props.selectedKinds}
            filterFeasability={props.selectedFeasabilities}
            filterDoneness={props.selectedDoneness}
            timeEventsByRefId={props.timeEventsByRefId}
          />
        </>
      )}

      {props.niceToHaveActivities.length > 0 && (
        <>
          <StandardDivider title="Nice To Have" size="large" />

          <TimePlanActivityList
            topLevelInfo={topLevelInfo}
            activities={props.niceToHaveActivities}
            inboxTasksByRefId={props.targetInboxTasksByRefId}
            timePlansByRefId={new Map()}
            bigPlansByRefId={props.targetBigPlansByRefId}
            activityDoneness={props.activityDoneness}
            fullInfo
            filterKind={props.selectedKinds}
            filterFeasability={props.selectedFeasabilities}
            filterDoneness={props.selectedDoneness}
            timeEventsByRefId={props.timeEventsByRefId}
          />
        </>
      )}

      {props.stretchActivities.length > 0 && (
        <>
          <StandardDivider title="Stretch" size="large" />

          <TimePlanActivityList
            topLevelInfo={topLevelInfo}
            activities={props.stretchActivities}
            inboxTasksByRefId={props.targetInboxTasksByRefId}
            timePlansByRefId={new Map()}
            bigPlansByRefId={props.targetBigPlansByRefId}
            activityDoneness={props.activityDoneness}
            fullInfo
            filterKind={props.selectedKinds}
            filterFeasability={props.selectedFeasabilities}
            filterDoneness={props.selectedDoneness}
            timeEventsByRefId={props.timeEventsByRefId}
          />
        </>
      )}
    </>
  );
}

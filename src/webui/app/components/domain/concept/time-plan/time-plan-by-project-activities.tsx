import { Fragment, useContext } from "react";
import type {
  TimePlanActivity,
  TimePlanActivityKind,
  TimePlanActivityFeasability,
  TimePlanActivityDoneness,
  InboxTask,
  BigPlan,
  TimeEventInDayBlock,
  ProjectSummary,
} from "@jupiter/webapi-client";
import { TimePlanActivityTarget } from "@jupiter/webapi-client";

import { StandardDivider } from "~/components/infra/standard-divider";
import { TimePlanActivityList } from "~/components/domain/concept/time-plan/time-plan-activity-list";
import { computeProjectHierarchicalNameFromRoot } from "~/logic/domain/project";
import { TopLevelInfoContext } from "~/top-level-context";

interface TimePlanByProjectActivitiesProps {
  mustDoActivities: TimePlanActivity[];
  otherActivities: TimePlanActivity[];
  targetInboxTasksByRefId: Map<string, InboxTask>;
  targetBigPlansByRefId: Map<string, BigPlan>;
  activityDoneness: Record<string, TimePlanActivityDoneness>;
  timeEventsByRefId: Map<string, TimeEventInDayBlock[]>;
  selectedKinds: TimePlanActivityKind[];
  selectedFeasabilities: TimePlanActivityFeasability[];
  selectedDoneness: boolean[];
  projects: ProjectSummary[];
  projectsByRefId: Map<string, ProjectSummary>;
}

export function TimePlanByProjectActivities(
  props: TimePlanByProjectActivitiesProps,
) {
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

      {props.projects.map((project) => {
        const projectActivities = props.otherActivities.filter((activity) => {
          switch (activity.target) {
            case TimePlanActivityTarget.INBOX_TASK:
              return (
                props.targetInboxTasksByRefId.get(activity.target_ref_id)
                  ?.project_ref_id === project.ref_id
              );
            case TimePlanActivityTarget.BIG_PLAN:
              return (
                props.targetBigPlansByRefId.get(activity.target_ref_id)
                  ?.project_ref_id === project.ref_id
              );
          }
          throw new Error("Should not get here");
        });

        if (projectActivities.length === 0) {
          return null;
        }

        const fullProjectName = computeProjectHierarchicalNameFromRoot(
          project,
          props.projectsByRefId,
        );

        return (
          <Fragment key={`project-${project.ref_id}`}>
            <StandardDivider title={fullProjectName} size="large" />

            <TimePlanActivityList
              topLevelInfo={topLevelInfo}
              activities={projectActivities}
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
          </Fragment>
        );
      })}
    </>
  );
}

import {
  InboxTask,
  TimePlan,
  TimePlanActivityDoneness,
  TimePlanActivity,
  BigPlan,
  TimePlanActivityFeasability,
  TimePlanActivityKind,
} from "@jupiter/webapi-client";
import { Stack } from "@mui/material";

import { DocsHelpSubject } from "~/components/infra/docs-help";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";
import { filterActivityByFeasabilityWithParents } from "~/logic/domain/time-plan-activity";
import { TimePlanMergedActivities } from "~/components/domain/concept/time-plan/time-plan-merged-activities";
import {
  WidgetContainer,
  WidgetProps,
} from "~/components/domain/application/home/common";

export function TimePlanViewWidget(props: WidgetProps) {
  const timePlans = props.timePlans!;

  if (!timePlans?.timePlanForToday && !timePlans?.timePlanForWeek) {
    return (
      <EntityNoNothingCard
        title="You Have To Start Somewhere"
        message="There are no time plans to show. You can create a new time plan."
        newEntityLocations={`/app/workspace/time-plans/new`}
        helpSubject={DocsHelpSubject.TIME_PLANS}
      />
    );
  }

  return (
    <Stack>
      {timePlans.timePlanForToday && (
        <SingleTimePlan
          timePlan={timePlans.timePlanForToday.timePlan}
          activities={timePlans.timePlanForToday.activities}
          targetInboxTasks={timePlans.timePlanForToday.targetInboxTasks}
          targetBigPlans={timePlans.timePlanForToday.targetBigPlans}
          activityDoneness={timePlans.timePlanForToday.activityDoneness}
        />
      )}
      {timePlans.timePlanForWeek && (
        <SingleTimePlan
          timePlan={timePlans.timePlanForWeek.timePlan}
          activities={timePlans.timePlanForWeek.activities}
          targetInboxTasks={timePlans.timePlanForWeek.targetInboxTasks}
          targetBigPlans={timePlans.timePlanForWeek.targetBigPlans}
          activityDoneness={timePlans.timePlanForWeek.activityDoneness}
        />
      )}
    </Stack>
  );
}

interface SingleTimePlanProps {
  timePlan: TimePlan;
  activities: TimePlanActivity[];
  targetInboxTasks: InboxTask[];
  targetBigPlans: BigPlan[];
  activityDoneness: Record<string, TimePlanActivityDoneness>;
}

function SingleTimePlan(props: SingleTimePlanProps) {
  const actitiviesByBigPlanRefId = new Map<string, TimePlanActivity>(
    props.activities.map((a) => [a.target_ref_id, a]),
  );
  const targetInboxTasksByRefId = new Map<string, InboxTask>(
    props.targetInboxTasks.map((it) => [it.ref_id, it]),
  );
  const targetBigPlansByRefId = new Map<string, BigPlan>(
    props.targetBigPlans.map((bp) => [bp.ref_id, bp]),
  );
  const mustDoActivities = filterActivityByFeasabilityWithParents(
    props.activities,
    actitiviesByBigPlanRefId,
    targetInboxTasksByRefId,
    targetBigPlansByRefId,
    TimePlanActivityFeasability.MUST_DO,
  );
  const niceToHaveActivities = filterActivityByFeasabilityWithParents(
    props.activities,
    actitiviesByBigPlanRefId,
    targetInboxTasksByRefId,
    targetBigPlansByRefId,
    TimePlanActivityFeasability.NICE_TO_HAVE,
  );
  const stretchActivities = filterActivityByFeasabilityWithParents(
    props.activities,
    actitiviesByBigPlanRefId,
    targetInboxTasksByRefId,
    targetBigPlansByRefId,
    TimePlanActivityFeasability.STRETCH,
  );

  if (props.activities.length === 0) {
    return (
      <EntityNoNothingCard
        title="You Have To Start Somewhere"
        message="There are no activities to show. You can create a new activity."
        newEntityLocations={`/app/workspace/time-plans/${props.timePlan.ref_id}/add-from-current-inbox-tasks`}
        helpSubject={DocsHelpSubject.TIME_PLANS}
      />
    );
  }

  return (
    <TimePlanMergedActivities
      mustDoActivities={mustDoActivities}
      niceToHaveActivities={niceToHaveActivities}
      stretchActivities={stretchActivities}
      targetInboxTasksByRefId={targetInboxTasksByRefId}
      targetBigPlansByRefId={targetBigPlansByRefId}
      activityDoneness={props.activityDoneness}
      timeEventsByRefId={new Map()}
      selectedKinds={Object.values(TimePlanActivityKind)}
      selectedFeasabilities={Object.values(TimePlanActivityFeasability)}
      selectedDoneness={[true, false]}
    />
  );
}

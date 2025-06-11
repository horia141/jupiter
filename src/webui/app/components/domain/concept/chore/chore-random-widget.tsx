import {
  InboxTaskSource,
  InboxTaskStatus,
  RecurringTaskPeriod,
} from "@jupiter/webapi-client";

import { filterInboxTasksForDisplay } from "~/logic/domain/inbox-task";
import { InboxTaskStack } from "~/components/domain/concept/inbox-task/inbox-task-stack";
import {
  ActionableTime,
  actionableTimeToDateTime,
} from "~/rendering/actionable-time";
import { InboxTasksNoTasksCard } from "~/components/domain/concept/inbox-task/inbox-tasks-no-tasks-card";
import {
  getDeterministicRandomElement,
  WidgetProps,
} from "~/components/domain/application/home/common";
import { aDateToDate } from "~/logic/domain/adate";

export function ChoreRandomWidget(props: WidgetProps) {
  const choreTasks = props.choreTasks!;
  const today = aDateToDate(props.topLevelInfo.today).endOf("day");
  const endOfTheMonth = today.endOf("month").endOf("day");
  const actionableTime = actionableTimeToDateTime(
    ActionableTime.ONE_WEEK,
    props.topLevelInfo.user.timezone,
  );

  // Get all chore tasks that are not done
  const allChoreTasks = filterInboxTasksForDisplay(
    choreTasks.choreInboxTasks,
    choreTasks.choreEntriesByRefId,
    choreTasks.optimisticUpdates,
    {
      allowSources: [InboxTaskSource.CHORE],
      allowStatuses: [
        InboxTaskStatus.NOT_STARTED,
        InboxTaskStatus.NOT_STARTED_GEN,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateEnd: endOfTheMonth,
      allowPeriodsIfChore: [
        RecurringTaskPeriod.DAILY,
        RecurringTaskPeriod.WEEKLY,
        RecurringTaskPeriod.MONTHLY,
      ],
    },
  );

  // If no tasks, show the no tasks card
  if (allChoreTasks.length === 0) {
    return (
      <InboxTasksNoTasksCard
        parent="chore"
        parentLabel="New Chore"
        parentNewLocations="/app/workspace/chores/new"
      />
    );
  }

  // Pick a random task
  const randomTask = getDeterministicRandomElement(allChoreTasks, props.topLevelInfo.today);

  return (
    <>
      <InboxTaskStack
        key="random-chore"
        topLevelInfo={props.topLevelInfo}
        showOptions={{
          showStatus: true,
          showProject: true,
          showEisen: true,
          showDifficulty: true,
          showParent: true,
          showHandleMarkDone: true,
          showHandleMarkNotDone: true,
        }}
        label="Do A Random Chore"
        inboxTasks={[randomTask]}
        optimisticUpdates={choreTasks.optimisticUpdates}
        moreInfoByRefId={choreTasks.choreEntriesByRefId}
        onCardMarkDone={choreTasks.onCardMarkDone}
        onCardMarkNotDone={choreTasks.onCardMarkNotDone}
      />
    </>
  );
}

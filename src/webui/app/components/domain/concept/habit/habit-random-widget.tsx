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

export function HabitRandomWidget(props: WidgetProps) {
  const habitTasks = props.habitTasks!;
  const today = aDateToDate(props.today).endOf("day");
  const endOfTheMonth = today.endOf("month").endOf("day");
  const actionableTime = actionableTimeToDateTime(
    ActionableTime.ONE_WEEK,
    props.topLevelInfo.user.timezone,
  );

  // Get all habit tasks that are not done
  const allHabitTasks = filterInboxTasksForDisplay(
    habitTasks.habitInboxTasks,
    habitTasks.habitEntriesByRefId,
    habitTasks.optimisticUpdates,
    {
      allowSources: [InboxTaskSource.HABIT],
      allowStatuses: [
        InboxTaskStatus.NOT_STARTED,
        InboxTaskStatus.NOT_STARTED_GEN,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateEnd: endOfTheMonth,
      allowPeriodsIfHabit: [
        RecurringTaskPeriod.DAILY,
        RecurringTaskPeriod.WEEKLY,
        RecurringTaskPeriod.MONTHLY,
      ],
    },
  );

  // If no tasks, show the no tasks card
  if (allHabitTasks.length === 0) {
    return (
      <InboxTasksNoTasksCard
        parent="habit"
        parentLabel="New Habit"
        parentNewLocations="/app/workspace/habits/new"
      />
    );
  }

  // Pick a random task
  const randomTask = getDeterministicRandomElement(allHabitTasks, props.today);

  return (
    <InboxTaskStack
      key="random-habit"
      today={today}
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
      label="Do A Random Habit"
      inboxTasks={[randomTask]}
      optimisticUpdates={habitTasks.optimisticUpdates}
      moreInfoByRefId={habitTasks.habitEntriesByRefId}
      onCardMarkDone={habitTasks.onCardMarkDone}
      onCardMarkNotDone={habitTasks.onCardMarkNotDone}
    />
  );
}

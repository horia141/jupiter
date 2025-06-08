import { InboxTaskSource, InboxTaskStatus } from "@jupiter/webapi-client";

import {
  filterInboxTasksForDisplay,
  sortInboxTasksByEisenAndDifficulty,
} from "~/logic/domain/inbox-task";
import { InboxTaskStack } from "~/components/domain/concept/inbox-task/inbox-task-stack";
import {
  ActionableTime,
  actionableTimeToDateTime,
} from "~/rendering/actionable-time";
import { InboxTasksNoTasksCard } from "~/components/domain/concept/inbox-task/inbox-tasks-no-tasks-card";
import {
  WidgetContainer,
  WidgetProps,
} from "~/components/domain/application/home/common";
import { aDateToDate } from "~/logic/domain/adate";

export function UpcomingBirthdaysWidget(props: WidgetProps) {
  const personTasks = props.personTasks!;
  const today = aDateToDate(props.today).endOf("day");
  const threeMonthsFromNow = today.plus({ months: 3 }).endOf("day");
  const actionableTime = actionableTimeToDateTime(
    ActionableTime.ONE_WEEK,
    props.topLevelInfo.user.timezone,
  );

  const sortedInboxTasks = sortInboxTasksByEisenAndDifficulty(
    personTasks.personInboxTasks,
  );

  const upcomingBirthdays = filterInboxTasksForDisplay(
    sortedInboxTasks,
    personTasks.personEntriesByRefId,
    personTasks.optimisticUpdates,
    {
      allowSources: [InboxTaskSource.PERSON_BIRTHDAY],
      allowStatuses: [
        InboxTaskStatus.NOT_STARTED,
        InboxTaskStatus.NOT_STARTED_GEN,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateEnd: threeMonthsFromNow,
    },
  );

  if (upcomingBirthdays.length === 0) {
    return (
      <WidgetContainer>
        <InboxTasksNoTasksCard
          parent="person"
          parentLabel="New Person"
          parentNewLocations="/app/workspace/persons/new"
        />
      </WidgetContainer>
    );
  }

  return (
    <WidgetContainer>
      <InboxTaskStack
        key="upcoming-birthdays"
        today={today}
        topLevelInfo={props.topLevelInfo}
        showOptions={{
          showStatus: true,
          showDueDate: true,
          showHandleMarkDone: true,
          showHandleMarkNotDone: true,
        }}
        label="Upcoming Birthdays"
        inboxTasks={upcomingBirthdays}
        optimisticUpdates={personTasks.optimisticUpdates}
        moreInfoByRefId={personTasks.personEntriesByRefId}
        onCardMarkDone={personTasks.onCardMarkDone}
        onCardMarkNotDone={personTasks.onCardMarkNotDone}
      />
    </WidgetContainer>
  );
}

import {
  ADate,
  InboxTask,
  MOTD,
  Timezone,
  TimePlanActivityDoneness,
  BigPlan,
  TimePlanActivity,
  TimePlan,
  CalendarEventsEntries,
  RecurringTaskPeriod,
  Habit,
  HabitStreakMark,
} from "@jupiter/webapi-client";
import { Box } from "@mui/material";
import { DateTime } from "luxon";
import { PropsWithChildren } from "react";

import {
  InboxTaskParent,
  InboxTaskOptimisticState,
} from "~/logic/domain/inbox-task";
import { TopLevelInfo } from "~/top-level-context";

interface HabitStreakEntry {
  habit: Habit;
  streakMarks: HabitStreakMark[];
  inboxTasks: InboxTask[];
}

export interface WidgetProps {
  rightNow: DateTime;
  today: ADate;
  timezone: Timezone;
  topLevelInfo: TopLevelInfo;
  motd?: MOTD;
  habitTasks?: {
    habits: Habit[];
    habitInboxTasks: InboxTask[];
    habitEntriesByRefId: { [key: string]: InboxTaskParent };
    optimisticUpdates: { [key: string]: InboxTaskOptimisticState };
    onCardMarkDone: (it: InboxTask) => void;
    onCardMarkNotDone: (it: InboxTask) => void;
  };
  habitStreak?: {
    year: number;
    currentYear: number;
    entries: HabitStreakEntry[];
    getYearUrl: (year: number) => string;
  };
  calendar?: {
    period: RecurringTaskPeriod;
    periodStartDate: ADate;
    periodEndDate: ADate;
    entries: CalendarEventsEntries;
  };
  timePlans?: {
    timePlanForToday?: {
      timePlan: TimePlan;
      activities: TimePlanActivity[];
      targetInboxTasks: InboxTask[];
      targetBigPlans: BigPlan[];
      activityDoneness: Record<string, TimePlanActivityDoneness>;
    };
    timePlanForWeek?: {
      timePlan: TimePlan;
      activities: TimePlanActivity[];
      targetInboxTasks: InboxTask[];
      targetBigPlans: BigPlan[];
      activityDoneness: Record<string, TimePlanActivityDoneness>;
    };
  };
}

export function WidgetContainer(props: PropsWithChildren) {
  return (
    <Box
      sx={{
        width: "100%",
        border: (theme) => `2px dotted ${theme.palette.primary.main}`,
        borderRadius: "4px",
        margin: "0.2rem",
        padding: "0.4rem",
      }}
    >
      {props.children}
    </Box>
  );
}

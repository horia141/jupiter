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
  UserScoreOverview,
  UserScoreHistory,
  BigPlanStats,
  WidgetType,
  WorkspaceFeature,
  UserFeature,
  WidgetGeometry,
  BigPlanMilestone,
} from "@jupiter/webapi-client";
import {
  Box,
  Card,
  CardHeader,
  CardContent,
  CardActions,
  Button,
  Typography,
} from "@mui/material";
import { DateTime } from "luxon";
import { PropsWithChildren } from "react";
import { Link } from "react-router-dom";

import {
  InboxTaskParent,
  InboxTaskOptimisticState,
} from "~/logic/domain/inbox-task";
import { TopLevelInfo } from "~/top-level-context";
import {
  isWidgetDimensionFlex,
  isWidgetDimensionKSized,
  widgetDimensionRows,
  widgetTypeName,
} from "~/logic/widget";
import { workspaceFeatureName, userFeatureName } from "~/logic/domain/feature";
import { useBigScreen } from "~/rendering/use-big-screen";

const WIDGET_HEIGHT_IN_REM_BASE = 14;

interface HabitStreakEntry {
  habit: Habit;
  streakMarks: HabitStreakMark[];
}

interface BigPlanEntry {
  bigPlan: BigPlan;
  stats: BigPlanStats;
  milestones: BigPlanMilestone[];
}

export interface WidgetProps {
  rightNow: DateTime;
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
  choreTasks?: {
    choreInboxTasks: InboxTask[];
    choreEntriesByRefId: { [key: string]: InboxTaskParent };
    optimisticUpdates: { [key: string]: InboxTaskOptimisticState };
    onCardMarkDone: (it: InboxTask) => void;
    onCardMarkNotDone: (it: InboxTask) => void;
  };
  personTasks?: {
    personInboxTasks: InboxTask[];
    personEntriesByRefId: { [key: string]: InboxTaskParent };
    optimisticUpdates: { [key: string]: InboxTaskOptimisticState };
    onCardMarkDone: (it: InboxTask) => void;
    onCardMarkNotDone: (it: InboxTask) => void;
  };
  habitStreak?: {
    earliestDate: ADate;
    latestDate: ADate;
    currentToday: ADate;
    entries: HabitStreakEntry[];
    showNav?: boolean;
    getNavUrl?: (earliestDate: ADate, latestDate: ADate) => string;
  };
  keyBigPlans?: {
    bigPlans: BigPlanEntry[];
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
  gamificationOverview?: UserScoreOverview;
  gamificationHistory?: UserScoreHistory;
  geometry: WidgetGeometry;
}

export type WidgetPropsNoGeometry = Omit<WidgetProps, "geometry">;

interface WidgetContainerProps {
  geometry: WidgetGeometry;
}

export function WidgetContainer(
  props: PropsWithChildren<WidgetContainerProps>,
) {
  const isBigScreen = useBigScreen();
  let heightInRem;
  let minHeightInRem;
  let maxHeightInRem;
  if (isWidgetDimensionKSized(props.geometry.dimension)) {
    heightInRem = undefined;
    minHeightInRem = undefined;
    maxHeightInRem = undefined;
  } else {
    if (isWidgetDimensionFlex(props.geometry.dimension)) {
      heightInRem = undefined;
      minHeightInRem = `${WIDGET_HEIGHT_IN_REM_BASE}rem`;
      maxHeightInRem = `${widgetDimensionRows(props.geometry.dimension) * WIDGET_HEIGHT_IN_REM_BASE}rem`;
    } else {
      heightInRem = `${widgetDimensionRows(props.geometry.dimension) * WIDGET_HEIGHT_IN_REM_BASE}rem`;
      minHeightInRem = `${widgetDimensionRows(props.geometry.dimension) * WIDGET_HEIGHT_IN_REM_BASE}rem`;
      maxHeightInRem = `${widgetDimensionRows(props.geometry.dimension) * WIDGET_HEIGHT_IN_REM_BASE}rem`;
    }
  }
  return (
    <Box
      sx={{
        width: isBigScreen ? "100%" : "calc(100% - 2 * 0.4rem)",
        height: heightInRem,
        minHeight: minHeightInRem,
        maxHeight: maxHeightInRem,
        border: (theme) => `2px dotted ${theme.palette.primary.main}`,
        borderRadius: "4px",
        margin: "0.2rem",
        padding: "0.4rem",
        overflowY: !isWidgetDimensionKSized(props.geometry.dimension)
          ? "scroll"
          : undefined,
      }}
    >
      {props.children}
    </Box>
  );
}

interface WidgetFeatureNotAvailableBannerProps {
  widgetType: WidgetType;
  missingWorkspaceFeatures: WorkspaceFeature[];
  missingUserFeatures: UserFeature[];
}

export function WidgetFeatureNotAvailableBanner(
  props: WidgetFeatureNotAvailableBannerProps,
) {
  const { widgetType, missingWorkspaceFeatures, missingUserFeatures } = props;

  const workspaceFeatureNames =
    missingWorkspaceFeatures.map(workspaceFeatureName);
  const userFeatureNames = missingUserFeatures.map(userFeatureName);

  const allFeatureNames = [...workspaceFeatureNames, ...userFeatureNames];
  const hasWorkspaceFeatures = missingWorkspaceFeatures.length > 0;
  const hasUserFeatures = missingUserFeatures.length > 0;

  return (
    <Card>
      <CardHeader title={`${widgetTypeName(widgetType)} Not Available`} />
      <CardContent>
        <Typography variant="body1">
          This widget requires the following features to be enabled:{" "}
          {allFeatureNames.join(", ")}
        </Typography>
      </CardContent>
      <CardActions>
        {hasWorkspaceFeatures && (
          <Button
            variant="contained"
            size="small"
            component={Link}
            to="/app/workspace/settings"
          >
            Enable Workspace Features
          </Button>
        )}
        {hasUserFeatures && (
          <Button
            variant="contained"
            size="small"
            component={Link}
            to="/app/workspace/account"
          >
            Enable User Features
          </Button>
        )}
      </CardActions>
    </Card>
  );
}

/**
 * Returns a deterministic random element from an array based on the given date.
 * The same date will always return the same element from the array.
 * @param array The array to select from
 * @param date The date to use as a seed
 * @returns A random element from the array
 */
export function getDeterministicRandomElement<T>(array: T[], date: ADate): T {
  if (array.length === 0) {
    throw new Error("Cannot select random element from empty array");
  }

  // Create a deterministic seed based on the date
  const seed = date
    .split("")
    .reduce((acc, char) => acc + char.charCodeAt(0), 0);

  // Use the seed to select an element
  const index = Math.abs(seed) % array.length;
  return array[index];
}

import { json, LoaderFunctionArgs } from "@remix-run/node";
import {
  Link,
  Outlet,
  useFetcher,
  useNavigation,
  useSearchParams,
  type ShouldRevalidateFunction,
} from "@remix-run/react";
import {
  BigScreenHomeTabWidgetPlacement,
  HabitLoadResult,
  HomeTab,
  HomeTabTarget,
  HomeWidget,
  InboxTask,
  InboxTaskSource,
  InboxTaskStatus,
  RecurringTaskPeriod,
  SmallScreenHomeTabWidgetPlacement,
  WidgetType,
  BigPlanLoadResult,
  InboxTaskFindResult,
  WorkspaceFeature,
  CalendarLoadForDateAndPeriodResult,
  WidgetTypeConstraints,
  User,
  Workspace,
} from "@jupiter/webapi-client";
import { Fragment, useContext, useEffect, useState } from "react";
import { DateTime } from "luxon";
import { AnimatePresence } from "framer-motion";
import TuneIcon from "@mui/icons-material/Tune";
import { z } from "zod";
import { parseQuery } from "zodix";
import { Tabs, Tab, Box } from "@mui/material";

import {
  useTrunkNeedsToShowLeaf,
  DisplayType,
} from "~/rendering/use-nested-entities";
import { getLoggedInApiClient } from "~/api-clients.server";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { makeRootErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { MOTDWidget } from "~/components/domain/concept/motd/motd-widget";
import {
  inboxTaskFindEntryToParent,
  InboxTaskOptimisticState,
  InboxTaskParent,
  sortInboxTasksNaturally,
} from "~/logic/domain/inbox-task";
import { TopLevelInfo, TopLevelInfoContext } from "~/top-level-context";
import { NavSingle, SectionActions } from "~/components/infra/section-actions";
import { newURLParams } from "~/logic/domain/navigation";
import { HabitInboxTasksWidget } from "~/components/domain/concept/habit/habit-inbox-tasks-widget";
import { TimePlanViewWidget } from "~/components/domain/concept/time-plan/time-plan-view-widget";
import { CalendarDailyWidget } from "~/components/domain/application/calendar/calendar-daily-widget";
import { HabitKeyHabitStreakWidget } from "~/components/domain/concept/habit/habit-key-habit-streak-widget";
import { useBigScreen } from "~/rendering/use-big-screen";
import {
  WidgetFeatureNotAvailableBanner,
  WidgetContainer,
  WidgetPropsNoGeometry,
} from "~/components/domain/application/home/common";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";
import { DocsHelpSubject } from "~/components/infra/docs-help";
import {
  widgetDimensionRows,
  widgetDimensionCols,
  isAllowedForWidgetConstraints,
} from "~/logic/widget";
import { ScheduleDailyWidget } from "~/components/domain/application/calendar/schedule-daily-widget";
import { HabitRandomWidget } from "~/components/domain/concept/habit/habit-random-widget";
import { ChoreInboxTasksWidget } from "~/components/domain/concept/chore/chore-inbox-tasks-widget";
import { ChoreRandomWidget } from "~/components/domain/concept/chore/chore-random-widget";
import { UpcomingBirthdaysWidget } from "~/components/domain/concept/person/upcoming-birthdays-widget";
import { GamificationOverviewWidget } from "~/components/domain/application/gamification/gamification-overview-widget";
import { GamificationHistoryWeeklyWidget } from "~/components/domain/application/gamification/gamification-history-weekly-widget";
import { GamificationHistoryMonthlyWidget } from "~/components/domain/application/gamification/gamification-history-monthly-widget";
import { KeyBigPlansProgressWidget } from "~/components/domain/concept/big-plan/key-big-plans-progress-widget";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { isUserFeatureAvailable } from "~/logic/domain/user";
import { sortAndFilterTabsByTheirOrder } from "~/logic/domain/home-tab";

export const handle = {
  displayType: DisplayType.TRUNK,
};

const QuerySchema = z.object({
  tabRefId: z.string().optional(),
});

export async function loader({ request }: LoaderFunctionArgs) {
  const rightNow = DateTime.now().toISODate();

  const apiClient = await getLoggedInApiClient(request);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_user: true,
    include_workspace: true,
    include_habits: true,
    include_chores: true,
    include_big_plans: true,
    include_persons: true,
  });

  const workspace = summaryResponse.workspace!;

  const homeConfigResponse = await apiClient.home.homeConfigLoad({});

  const motdResponse = await apiClient.motd.motdGetForToday({});

  let keyHabitResults: HabitLoadResult[] | undefined = undefined;
  let habitInboxTasksResponse: InboxTaskFindResult | undefined = undefined;

  if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.HABITS)) {
    const keyHabits = summaryResponse.habits?.filter((h) => h.is_key) || [];

    const earliestDate = DateTime.now().minus({ days: 365 }).toISODate();
    const latestDate = DateTime.now().toISODate();

    keyHabitResults = [];
    if (keyHabits.length > 0) {
      keyHabitResults = await Promise.all(
        keyHabits.map((habit) =>
          apiClient.habits.habitLoad({
            ref_id: habit.ref_id,
            allow_archived: false,
            include_streak_marks_earliest_date: earliestDate,
            include_streak_marks_latest_date: latestDate,
          }),
        ),
      );
    }

    habitInboxTasksResponse = await apiClient.inboxTasks.inboxTaskFind({
      allow_archived: false,
      include_notes: false,
      include_time_event_blocks: false,
      filter_sources: [InboxTaskSource.HABIT],
    });
  }

  let choreInboxTasksResponse: InboxTaskFindResult | undefined = undefined;

  if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.CHORES)) {
    choreInboxTasksResponse = await apiClient.inboxTasks.inboxTaskFind({
      allow_archived: false,
      include_notes: false,
      include_time_event_blocks: false,
      filter_sources: [InboxTaskSource.CHORE],
    });
  }

  let keyBigPlansResults: BigPlanLoadResult[] | undefined = undefined;

  if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.BIG_PLANS)) {
    const keyBigPlans =
      summaryResponse.big_plans?.filter((bp) => bp.is_key) || [];
    keyBigPlansResults = [];
    if (keyBigPlans.length > 0) {
      keyBigPlansResults = await Promise.all(
        keyBigPlans.map((bp) =>
          apiClient.bigPlans.bigPlanLoad({
            ref_id: bp.ref_id,
            allow_archived: false,
          }),
        ),
      );
    }
  }

  let personInboxTasksResponse: InboxTaskFindResult | undefined = undefined;

  if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.PERSONS)) {
    personInboxTasksResponse = await apiClient.inboxTasks.inboxTaskFind({
      allow_archived: false,
      include_notes: false,
      include_time_event_blocks: false,
      filter_sources: [InboxTaskSource.PERSON_BIRTHDAY],
    });
  }

  let calendarForTodayResponse: CalendarLoadForDateAndPeriodResult | undefined =
    undefined;

  if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SCHEDULE)) {
    calendarForTodayResponse =
      await apiClient.calendar.calendarLoadForDateAndPeriod({
        right_now: rightNow,
        period: RecurringTaskPeriod.DAILY,
        stats_subperiod: null,
      });
  }

  let fullTimePlanForToday = null;

  if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.TIME_PLANS)) {
    const timePlanForTodayResponse =
      await apiClient.timePlans.timePlanLoadForTimeDateAndPeriod({
        right_now: rightNow,
        period: RecurringTaskPeriod.DAILY,
        allow_archived: false,
      });

    if (timePlanForTodayResponse.time_plan) {
      fullTimePlanForToday = await apiClient.timePlans.timePlanLoad({
        ref_id: timePlanForTodayResponse.time_plan.ref_id,
        allow_archived: false,
        include_targets: true,
        include_completed_nontarget: false,
        include_other_time_plans: false,
      });
    }
  }

  let fullTimePlanForWeek = null;

  if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.TIME_PLANS)) {
    const timePlanForWeekResponse =
      await apiClient.timePlans.timePlanLoadForTimeDateAndPeriod({
        right_now: rightNow,
        period: RecurringTaskPeriod.WEEKLY,
        allow_archived: false,
      });

    if (timePlanForWeekResponse.time_plan) {
      fullTimePlanForWeek = await apiClient.timePlans.timePlanLoad({
        ref_id: timePlanForWeekResponse.time_plan.ref_id,
        allow_archived: false,
        include_targets: true,
        include_completed_nontarget: false,
        include_other_time_plans: false,
      });
    }
  }

  const userResponse = await apiClient.users.userLoad({});

  return json({
    homeConfig: {
      config: homeConfigResponse.home_config,
      tabs: homeConfigResponse.tabs,
      widgets: homeConfigResponse.widgets,
      widgetConstraints: homeConfigResponse.widget_constraints,
    },
    motd: motdResponse.motd,
    habitInboxTasks: habitInboxTasksResponse?.entries,
    choreInboxTasks: choreInboxTasksResponse?.entries,
    personInboxTasks: personInboxTasksResponse?.entries,
    keyHabitResults: keyHabitResults?.map((h) => ({
      habit: h.habit,
      streakMarkEarliestDate: h.streak_mark_earliest_date,
      streakMarkLatestDate: h.streak_mark_latest_date,
      streakMarks: h.streak_marks,
    })),
    keyBigPlansResults: keyBigPlansResults?.map((bp) => ({
      bigPlan: bp.big_plan,
      stats: bp.stats,
      milestones: bp.milestones,
    })),
    calendarEntriesForToday: calendarForTodayResponse?.entries,
    timePlanForToday: fullTimePlanForToday
      ? {
          timePlan: fullTimePlanForToday.time_plan,
          activities: fullTimePlanForToday.activities,
          targetInboxTasks: fullTimePlanForToday.target_inbox_tasks ?? [],
          targetBigPlans: fullTimePlanForToday.target_big_plans ?? [],
          activityDoneness: fullTimePlanForToday.activity_doneness ?? {},
        }
      : undefined,
    timePlanForWeek: fullTimePlanForWeek
      ? {
          timePlan: fullTimePlanForWeek.time_plan,
          activities: fullTimePlanForWeek.activities,
          targetInboxTasks: fullTimePlanForWeek.target_inbox_tasks ?? [],
          targetBigPlans: fullTimePlanForWeek.target_big_plans ?? [],
          activityDoneness: fullTimePlanForWeek.activity_doneness ?? {},
        }
      : undefined,
    gamificationOverview: userResponse.user_score_overview,
    gamificationHistory: userResponse.user_score_history,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction = ({
  currentUrl,
  defaultShouldRevalidate,
  formAction,
  formMethod,
  nextUrl,
}) => {
  if (currentUrl.pathname === nextUrl.pathname) {
    return false;
  }

  return standardShouldRevalidate({
    currentUrl,
    defaultShouldRevalidate,
    formAction,
    formMethod,
    nextUrl,
    currentParams: {},
    nextParams: {},
  });
};

export default function WorkspaceHome() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const navigation = useNavigation();
  const inputsEnabled = navigation.state === "loading" ? false : true;
  const shouldShowALeaf = useTrunkNeedsToShowLeaf();
  const isBigScreen = useBigScreen();

  const sortedHabitInboxTasks = loaderData.habitInboxTasks
    ? sortInboxTasksNaturally(
        loaderData.habitInboxTasks.map((e) => e.inbox_task),
      )
    : undefined;
  const habitInboxTasksByRefId: { [key: string]: InboxTask } = {};
  if (loaderData.habitInboxTasks) {
    for (const entry of loaderData.habitInboxTasks) {
      habitInboxTasksByRefId[entry.inbox_task.ref_id] = entry.inbox_task;
    }
  }
  const habitEntriesByRefId: { [key: string]: InboxTaskParent } = {};
  if (loaderData.habitInboxTasks) {
    for (const entry of loaderData.habitInboxTasks) {
      habitEntriesByRefId[entry.inbox_task.ref_id] =
        inboxTaskFindEntryToParent(entry);
    }
  }

  const sortedChoreInboxTasks = loaderData.choreInboxTasks
    ? sortInboxTasksNaturally(
        loaderData.choreInboxTasks.map((e) => e.inbox_task),
      )
    : undefined;
  const choreInboxTasksByRefId: { [key: string]: InboxTask } = {};
  if (loaderData.choreInboxTasks) {
    for (const entry of loaderData.choreInboxTasks) {
      choreInboxTasksByRefId[entry.inbox_task.ref_id] = entry.inbox_task;
    }
  }
  const choreEntriesByRefId: { [key: string]: InboxTaskParent } = {};
  if (loaderData.choreInboxTasks) {
    for (const entry of loaderData.choreInboxTasks) {
      choreEntriesByRefId[entry.inbox_task.ref_id] =
        inboxTaskFindEntryToParent(entry);
    }
  }

  const sortedPersonInboxTasks = loaderData.personInboxTasks
    ? sortInboxTasksNaturally(
        loaderData.personInboxTasks.map((e) => e.inbox_task),
      )
    : undefined;
  const personInboxTasksByRefId: { [key: string]: InboxTask } = {};
  if (loaderData.personInboxTasks) {
    for (const entry of loaderData.personInboxTasks) {
      personInboxTasksByRefId[entry.inbox_task.ref_id] = entry.inbox_task;
    }
  }

  const personEntriesByRefId: { [key: string]: InboxTaskParent } = {};
  if (loaderData.personInboxTasks) {
    for (const entry of loaderData.personInboxTasks) {
      personEntriesByRefId[entry.inbox_task.ref_id] =
        inboxTaskFindEntryToParent(entry);
    }
  }

  const [optimisticUpdates, setOptimisticUpdates] = useState<{
    [key: string]: InboxTaskOptimisticState;
  }>({});

  const kanbanBoardMoveFetcher = useFetcher();

  const rightNow = DateTime.local({ zone: topLevelInfo.user.timezone });
  const today = rightNow.toISODate();

  const bigScreenTabs = sortAndFilterTabsByTheirOrder(
    loaderData.homeConfig.config,
    HomeTabTarget.BIG_SCREEN,
    loaderData.homeConfig.tabs
  );
  const smallScreenTabs = sortAndFilterTabsByTheirOrder(
    loaderData.homeConfig.config,
    HomeTabTarget.SMALL_SCREEN,
    loaderData.homeConfig.tabs
  );

  const widgetByRefId = new Map(
    loaderData.homeConfig.widgets.map((w) => [w.ref_id, w]),
  );

  function handleCardMarkDone(it: InboxTask) {
    setOptimisticUpdates((oldOptimisticUpdates) => {
      return {
        ...oldOptimisticUpdates,
        [it.ref_id]: {
          status: InboxTaskStatus.DONE,
          eisen: oldOptimisticUpdates[it.ref_id]?.eisen ?? it.eisen,
        },
      };
    });

    setTimeout(() => {
      kanbanBoardMoveFetcher.submit(
        {
          id: it.ref_id,
          status: InboxTaskStatus.DONE,
        },
        {
          method: "post",
          action: "/app/workspace/inbox-tasks/update-status-and-eisen",
        },
      );
    }, 0);
  }

  function handleCardMarkNotDone(it: InboxTask) {
    setOptimisticUpdates((oldOptimisticUpdates) => {
      return {
        ...oldOptimisticUpdates,
        [it.ref_id]: {
          status: InboxTaskStatus.NOT_DONE,
          eisen: oldOptimisticUpdates[it.ref_id]?.eisen ?? it.eisen,
        },
      };
    });

    setTimeout(() => {
      kanbanBoardMoveFetcher.submit(
        {
          id: it.ref_id,
          status: InboxTaskStatus.NOT_DONE,
        },
        {
          method: "post",
          action: "/app/workspace/inbox-tasks/update-status-and-eisen",
        },
      );
    }, 0);
  }

  const widgetProps: WidgetPropsNoGeometry = {
    rightNow,
    timezone: topLevelInfo.user.timezone,
    topLevelInfo,
    motd: loaderData.motd,
    habitTasks: loaderData.keyHabitResults
      ? {
          habits: loaderData.keyHabitResults.map((h) => h.habit),
          habitInboxTasks: sortedHabitInboxTasks!,
          habitEntriesByRefId: habitEntriesByRefId!,
          optimisticUpdates,
          onCardMarkDone: handleCardMarkDone,
          onCardMarkNotDone: handleCardMarkNotDone,
        }
      : undefined,
    choreTasks: loaderData.choreInboxTasks
      ? {
          choreInboxTasks: sortedChoreInboxTasks!,
          choreEntriesByRefId: choreEntriesByRefId!,
          optimisticUpdates,
          onCardMarkDone: handleCardMarkDone,
          onCardMarkNotDone: handleCardMarkNotDone,
        }
      : undefined,
    personTasks: loaderData.personInboxTasks
      ? {
          personInboxTasks: sortedPersonInboxTasks!,
          personEntriesByRefId: personEntriesByRefId!,
          optimisticUpdates,
          onCardMarkDone: handleCardMarkDone,
          onCardMarkNotDone: handleCardMarkNotDone,
        }
      : undefined,
    habitStreak: loaderData.keyHabitResults
      ? {
          earliestDate:
            loaderData.keyHabitResults[0]?.streakMarkEarliestDate ??
            topLevelInfo.today,
          latestDate:
            loaderData.keyHabitResults[0]?.streakMarkLatestDate ??
            topLevelInfo.today,
          currentToday: topLevelInfo.today,
          entries: loaderData.keyHabitResults,
          label: "Last Quarter",
        }
      : undefined,
    keyBigPlans: loaderData.keyBigPlansResults
      ? {
          bigPlans: loaderData.keyBigPlansResults.map((bp) => ({
            bigPlan: bp.bigPlan,
            stats: bp.stats,
            milestones: bp.milestones,
          })),
        }
      : undefined,
    calendar: loaderData.calendarEntriesForToday
      ? {
          period: RecurringTaskPeriod.DAILY,
          periodStartDate: today,
          periodEndDate: today,
          entries: loaderData.calendarEntriesForToday,
        }
      : undefined,
    timePlans: {
      timePlanForToday: loaderData.timePlanForToday,
      timePlanForWeek: loaderData.timePlanForWeek,
    },
    gamificationOverview: loaderData.gamificationOverview ?? undefined,
    gamificationHistory: loaderData.gamificationHistory ?? undefined,
  };

  return (
    <TrunkPanel
      key={"workspace"}
      returnLocation="/app/workspace"
      actions={
        <SectionActions
          id="home-actions"
          topLevelInfo={topLevelInfo}
          inputsEnabled={inputsEnabled}
          actions={[
            NavSingle({
              text: "Settings",
              icon: <TuneIcon />,
              link: "/app/workspace/home/settings",
            }),
          ]}
        />
      }
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        {isBigScreen && (
          <>
            {bigScreenTabs.length === 0 && (
              <EntityNoNothingCard
                title="You Have To Start Somewhere"
                message="There are no tabs to show for the big screen. You can create a new tab."
                newEntityLocations="/app/workspace/home/settings/tabs/new"
                helpSubject={DocsHelpSubject.HOME}
              />
            )}

            {bigScreenTabs.length > 0 && (
              <BigScreenTabs
                topLevelInfo={topLevelInfo}
                widgetConstraints={loaderData.homeConfig.widgetConstraints}
                bigScreenTabs={bigScreenTabs}
                widgetByRefId={widgetByRefId}
                widgetProps={widgetProps}
              />
            )}
          </>
        )}

        {!isBigScreen && (
          <>
            {smallScreenTabs.length === 0 && (
              <EntityNoNothingCard
                title="You Have To Start Somewhere"
                message="There are no tabs to show for the small screen. You can create a new tab."
                newEntityLocations="/app/workspace/home/settings/tabs/new"
                helpSubject={DocsHelpSubject.HOME}
              />
            )}

            {smallScreenTabs.length > 0 && (
              <SmallScreenTabs
                topLevelInfo={topLevelInfo}
                widgetConstraints={loaderData.homeConfig.widgetConstraints}
                smallScreenTabs={smallScreenTabs}
                widgetByRefId={widgetByRefId}
                widgetProps={widgetProps}
              />
            )}
          </>
        )}
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeRootErrorBoundary({
  error: () => `There was an error loading the workspace! Please try again!`,
});

interface BigScreenTabsProps {
  topLevelInfo: TopLevelInfo;
  widgetConstraints: Record<string, WidgetTypeConstraints>;
  bigScreenTabs: HomeTab[];
  widgetByRefId: Map<string, HomeWidget>;
  widgetProps: WidgetPropsNoGeometry;
}

function BigScreenTabs(props: BigScreenTabsProps) {
  const [query] = useSearchParams();
  const { tabRefId } = parseQuery(query, QuerySchema);
  const [bigScreenTab, setBigScreenTab] = useState<string>(
    inferCurrentTabs(props.bigScreenTabs, tabRefId),
  );

  useEffect(() => {
    setBigScreenTab(inferCurrentTabs(props.bigScreenTabs, tabRefId));
  }, [tabRefId, props.bigScreenTabs]);

  return (
    <>
      <Tabs value={bigScreenTab} variant="scrollable" scrollButtons="auto">
        {props.bigScreenTabs.map((t) => {
          return (
            <Tab
              key={t.ref_id}
              icon={<p>{t.icon}</p>}
              iconPosition="top"
              label={t.name}
              value={t.ref_id}
              component={Link}
              to={`/app/workspace?${newURLParams(query, "tabRefId", t.ref_id)}`}
              replace
            />
          );
        })}
      </Tabs>

      {props.bigScreenTabs.map((t) => {
        if (t.ref_id !== bigScreenTab) {
          return null;
        }

        const widgetPlacement =
          t.widget_placement as BigScreenHomeTabWidgetPlacement;

        if (widgetPlacement.matrix.every((r) => r.every((c) => c === null))) {
          return (
            <EntityNoNothingCard
              key={t.ref_id}
              title="You Have To Start Somewhere"
              message="There are no widgets to show. You can create a new widget."
              newEntityLocations={`/app/workspace/home/settings/tabs/${t.ref_id}`}
              helpSubject={DocsHelpSubject.HOME}
            />
          );
        }

        const maxCols = widgetPlacement.matrix.length;
        const maxRows = widgetPlacement.matrix[0].length;

        return (
          <Box
            key={t.ref_id}
            sx={{
              display: "grid",
              gridTemplateColumns: `repeat(${maxCols}, 1fr)`,
              gridGap: "0.25rem",
              alignItems: "flex-start",
              marginLeft: "auto",
              marginRight: "auto",
            }}
          >
            {Array.from({ length: maxRows }, (_, rowIndex) => {
              return (
                <Fragment key={rowIndex}>
                  {Array.from({ length: maxCols }, (_, colIndex) => {
                    const cell = widgetPlacement.matrix[colIndex][rowIndex];

                    if (cell === null) {
                      return null;
                    }

                    // If the previous widget is the same as the current one, don't render the current block,
                    // since this is a bigger widget that is taking up the space of the smaller one.
                    // We check both the row and the column to make sure we don't render the same widget twice.
                    if (
                      rowIndex > 0 &&
                      widgetPlacement.matrix[colIndex][rowIndex] ===
                        widgetPlacement.matrix[colIndex][rowIndex - 1]
                    ) {
                      return null;
                    }

                    if (
                      colIndex > 0 &&
                      widgetPlacement.matrix[colIndex][rowIndex] ===
                        widgetPlacement.matrix[colIndex - 1][rowIndex]
                    ) {
                      return null;
                    }

                    const widget = props.widgetByRefId.get(cell)!;
                    const isLastInColumn =
                      rowIndex ===
                        widgetPlacement.matrix[colIndex].length - 1 ||
                      widgetPlacement.matrix[colIndex].every(
                        (w, idx) =>
                          idx <=
                            rowIndex +
                              widgetDimensionRows(widget!.geometry.dimension) -
                              1 || w === null,
                      );
                    const shouldBeFullWidget = !isLastInColumn;

                    return (
                      <Box
                        key={`${rowIndex}-${colIndex}`}
                        sx={{
                          display: "flex",
                          height: shouldBeFullWidget ? "100%" : undefined,
                          gridRowStart: rowIndex + 1,
                          gridRowEnd:
                            rowIndex +
                            1 +
                            widgetDimensionRows(widget!.geometry.dimension),
                          gridColumnStart: colIndex + 1,
                          gridColumnEnd:
                            colIndex +
                            1 +
                            widgetDimensionCols(widget!.geometry.dimension),
                        }}
                      >
                        <ActualWidget
                          widget={widget}
                          widgetProps={props.widgetProps}
                          widgetConstraints={props.widgetConstraints}
                          user={props.topLevelInfo.user}
                          workspace={props.topLevelInfo.workspace}
                        />
                      </Box>
                    );
                  })}
                </Fragment>
              );
            })}
          </Box>
        );
      })}
    </>
  );
}

interface SmallScreenTabsProps {
  topLevelInfo: TopLevelInfo;
  widgetConstraints: Record<string, WidgetTypeConstraints>;
  smallScreenTabs: HomeTab[];
  widgetByRefId: Map<string, HomeWidget>;
  widgetProps: WidgetPropsNoGeometry;
}

function SmallScreenTabs(props: SmallScreenTabsProps) {
  const [query] = useSearchParams();
  const { tabRefId } = parseQuery(query, QuerySchema);
  const [mobileTab, setMobileTab] = useState<string>(
    inferCurrentTabs(props.smallScreenTabs, tabRefId),
  );

  useEffect(() => {
    setMobileTab(inferCurrentTabs(props.smallScreenTabs, tabRefId));
  }, [tabRefId, props.smallScreenTabs]);

  return (
    <>
      <Tabs value={mobileTab} variant="scrollable" scrollButtons="auto">
        {props.smallScreenTabs.map((t) => {
          return (
            <Tab
              key={t.ref_id}
              icon={<p>{t.icon}</p>}
              iconPosition="top"
              label={t.name}
              value={t.ref_id}
              component={Link}
              to={`/app/workspace?${newURLParams(query, "tabRefId", t.ref_id)}`}
              replace
            />
          );
        })}
      </Tabs>

      {props.smallScreenTabs.map((t) => {
        if (t.ref_id !== mobileTab) {
          return null;
        }

        const widgetPlacement =
          t.widget_placement as SmallScreenHomeTabWidgetPlacement;

        if (widgetPlacement.matrix.every((r) => r === null)) {
          return (
            <EntityNoNothingCard
              key={t.ref_id}
              title="You Have To Start Somewhere"
              message="There are no widgets to show. You can create a new widget."
              newEntityLocations={`/app/workspace/home/settings/tabs/${t.ref_id}`}
              helpSubject={DocsHelpSubject.HOME}
            />
          );
        }

        return (
          <Fragment key={t.ref_id}>
            {widgetPlacement.matrix.map((row, rowIndex) => {
              if (row === null) {
                return null;
              }

              // If the previous widget is the same as the current one, don't render the current block,
              // since this is a bigger widget that is taking up the space of the smaller one.
              if (
                rowIndex > 0 &&
                widgetPlacement.matrix[rowIndex] ===
                  widgetPlacement.matrix[rowIndex - 1]
              ) {
                return null;
              }

              const widget = props.widgetByRefId.get(row)!;

              return (
                <ActualWidget
                  key={rowIndex}
                  widget={widget}
                  widgetProps={props.widgetProps}
                  widgetConstraints={props.widgetConstraints}
                  user={props.topLevelInfo.user}
                  workspace={props.topLevelInfo.workspace}
                />
              );
            })}
          </Fragment>
        );
      })}
    </>
  );
}

interface ActualWidgetProps {
  widget: HomeWidget;
  widgetProps: WidgetPropsNoGeometry;
  widgetConstraints: Record<WidgetType, WidgetTypeConstraints>;
  user: User;
  workspace: Workspace;
}

function ActualWidget({
  widget,
  widgetProps,
  widgetConstraints,
  user,
  workspace,
}: ActualWidgetProps) {
  const constraint = widgetConstraints[widget.the_type];
  if (!constraint) {
    return <div>Not implemented</div>;
  }

  if (!isAllowedForWidgetConstraints(constraint, user, workspace)) {
    const workspaceFeatures = constraint.only_for_workspace_features || [];
    const userFeatures = constraint.only_for_user_features || [];

    const missingWorkspaceFeatures = workspaceFeatures.filter(
      (feature) => !isWorkspaceFeatureAvailable(workspace, feature),
    );
    const missingUserFeatures = userFeatures.filter(
      (feature) => !isUserFeatureAvailable(user, feature),
    );

    return (
      <WidgetFeatureNotAvailableBanner
        widgetType={widget.the_type}
        missingWorkspaceFeatures={missingWorkspaceFeatures}
        missingUserFeatures={missingUserFeatures}
      />
    );
  }

  return (
    <WidgetContainer geometry={widget.geometry}>
      <ActualWidgetItself widget={widget} widgetProps={widgetProps} />
    </WidgetContainer>
  );
}

interface ActualWidgetItselfProps {
  widget: HomeWidget;
  widgetProps: WidgetPropsNoGeometry;
}

function ActualWidgetItself({ widget, widgetProps }: ActualWidgetItselfProps) {
  const widgetPropsWithGeometry = {
    ...widgetProps,
    geometry: widget.geometry,
  };

  switch (widget.the_type) {
    case WidgetType.MOTD:
      return <MOTDWidget {...widgetPropsWithGeometry} />;
    case WidgetType.WORKING_MEM:
      return <div>Not implemented</div>;
    case WidgetType.KEY_HABITS_STREAKS:
      return <HabitKeyHabitStreakWidget {...widgetPropsWithGeometry} />;
    case WidgetType.HABIT_INBOX_TASKS:
      return <HabitInboxTasksWidget {...widgetPropsWithGeometry} />;
    case WidgetType.RANDOM_HABIT:
      return <HabitRandomWidget {...widgetPropsWithGeometry} />;
    case WidgetType.CHORE_INBOX_TASKS:
      return <ChoreInboxTasksWidget {...widgetPropsWithGeometry} />;
    case WidgetType.RANDOM_CHORE:
      return <ChoreRandomWidget {...widgetPropsWithGeometry} />;
    case WidgetType.KEY_BIG_PLANS_PROGRESS:
      return <KeyBigPlansProgressWidget {...widgetPropsWithGeometry} />;
    case WidgetType.UPCOMING_BIRTHDAYS:
      return <UpcomingBirthdaysWidget {...widgetPropsWithGeometry} />;
    case WidgetType.CALENDAR_DAY:
      return <CalendarDailyWidget {...widgetPropsWithGeometry} />;
    case WidgetType.SCHEDULE_DAY:
      return <ScheduleDailyWidget {...widgetPropsWithGeometry} />;
    case WidgetType.TIME_PLAN_VIEW:
      return <TimePlanViewWidget {...widgetPropsWithGeometry} />;
    case WidgetType.GAMIFICATION_OVERVIEW:
      return <GamificationOverviewWidget {...widgetPropsWithGeometry} />;
    case WidgetType.GAMIFICATION_HISTORY_WEEKLY:
      return <GamificationHistoryWeeklyWidget {...widgetPropsWithGeometry} />;
    case WidgetType.GAMIFICATION_HISTORY_MONTHLY:
      return <GamificationHistoryMonthlyWidget {...widgetPropsWithGeometry} />;
  }
}

function inferCurrentTabs(tabs: HomeTab[], tabRefId?: string): string {
  if (tabRefId) {
    const tab = tabs.find((t) => t.ref_id === tabRefId);
    if (tab) {
      return tab.ref_id;
    }
  }

  return tabs[0].ref_id;
}

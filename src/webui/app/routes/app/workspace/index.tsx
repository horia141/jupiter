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
import { TopLevelInfoContext } from "~/top-level-context";
import { NavSingle, SectionActions } from "~/components/infra/section-actions";
import { newURLParams } from "~/logic/domain/navigation";
import { HabitInboxTasksWidget } from "~/components/domain/concept/habit/habit-inbox-tasks-widget";
import { TimePlanViewWidget } from "~/components/domain/concept/time-plan/time-plan-view-widget";
import { CalendarDailyWidget } from "~/components/domain/application/calendar/calendar-daily-widget";
import { HabitKeyHabitStreakWidget } from "~/components/domain/concept/habit/habit-key-habit-streak-widget";
import { useBigScreen } from "~/rendering/use-big-screen";
import { WidgetProps } from "~/components/domain/application/home/common";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";
import { DocsHelpSubject } from "~/components/infra/docs-help";
import {
  widgetDimensionRows,
  widgetDimensionCols,
} from "~/logic/widget";

export const handle = {
  displayType: DisplayType.TRUNK,
};

const QuerySchema = z.object({
  tabRefId: z.string().optional(),
  includeStreakMarksForYear: z
    .string()
    .transform((s) => parseInt(s, 10))
    .optional(),
});

export async function loader({ request }: LoaderFunctionArgs) {
  const query = parseQuery(request, QuerySchema);
  const rightNow = DateTime.now().toISODate();

  const apiClient = await getLoggedInApiClient(request);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_habits: true,
  });

  const homeConfigResponse = await apiClient.home.homeConfigLoad({});

  const keyHabits = summaryResponse.habits?.filter((h) => h.is_key) || [];

  let keyHabitResults: HabitLoadResult[] = [];
  if (keyHabits.length > 0) {
    keyHabitResults = await Promise.all(
      keyHabits.map((habit) =>
        apiClient.habits.habitLoad({
          ref_id: habit.ref_id,
          allow_archived: false,
          include_streak_marks_for_year: query.includeStreakMarksForYear,
        }),
      ),
    );
  }

  const motdResponse = await apiClient.motd.motdGetForToday({});

  const habitInboxTasksResponse = await apiClient.inboxTasks.inboxTaskFind({
    allow_archived: false,
    include_notes: false,
    include_time_event_blocks: false,
    filter_sources: [InboxTaskSource.HABIT],
  });

  const calendarForTodayResponse =
    await apiClient.calendar.calendarLoadForDateAndPeriod({
      right_now: rightNow,
      period: RecurringTaskPeriod.DAILY,
      stats_subperiod: null,
    });
  const timePlanForTodayResponse =
    await apiClient.timePlans.timePlanLoadForTimeDateAndPeriod({
      right_now: rightNow,
      period: RecurringTaskPeriod.DAILY,
      allow_archived: false,
    });
  let fullTimePlanForToday = null;
  if (timePlanForTodayResponse.time_plan) {
    fullTimePlanForToday = await apiClient.timePlans.timePlanLoad({
      ref_id: timePlanForTodayResponse.time_plan.ref_id,
      allow_archived: false,
      include_targets: true,
      include_completed_nontarget: false,
      include_other_time_plans: false,
    });
  }

  const timePlanForWeekResponse =
    await apiClient.timePlans.timePlanLoadForTimeDateAndPeriod({
      right_now: rightNow,
      period: RecurringTaskPeriod.WEEKLY,
      allow_archived: false,
    });

  let fullTimePlanForWeek = null;
  if (timePlanForWeekResponse.time_plan) {
    fullTimePlanForWeek = await apiClient.timePlans.timePlanLoad({
      ref_id: timePlanForWeekResponse.time_plan.ref_id,
      allow_archived: false,
      include_targets: true,
      include_completed_nontarget: false,
      include_other_time_plans: false,
    });
  }

  return json({
    homeConfig: {
      config: homeConfigResponse.home_config,
      tabs: homeConfigResponse.tabs,
      widgets: homeConfigResponse.widgets,
    },
    motd: motdResponse.motd,
    habitInboxTasks: habitInboxTasksResponse.entries,
    keyHabitResults: keyHabitResults.map((h) => ({
      habit: h.habit,
      streakMarkYear: h.streak_mark_year,
      streakMarks: h.streak_marks,
      inboxTasks: h.inbox_tasks,
    })),
    calendarEntriesForToday: calendarForTodayResponse.entries,
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
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Workspace() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const navigation = useNavigation();
  const inputsEnabled = navigation.state === "loading" ? false : true;
  const [query] = useSearchParams();
  const shouldShowALeaf = useTrunkNeedsToShowLeaf();
  const isBigScreen = useBigScreen();

  const sortedHabitInboxTasks = sortInboxTasksNaturally(
    loaderData.habitInboxTasks.map((e) => e.inbox_task),
  );
  const habitInboxTasksByRefId: { [key: string]: InboxTask } = {};
  for (const entry of loaderData.habitInboxTasks) {
    habitInboxTasksByRefId[entry.inbox_task.ref_id] = entry.inbox_task;
  }
  const habitEntriesByRefId: { [key: string]: InboxTaskParent } = {};
  for (const entry of loaderData.habitInboxTasks) {
    habitEntriesByRefId[entry.inbox_task.ref_id] =
      inboxTaskFindEntryToParent(entry);
  }
  const [optimisticUpdates, setOptimisticUpdates] = useState<{
    [key: string]: InboxTaskOptimisticState;
  }>({});

  const kanbanBoardMoveFetcher = useFetcher();

  const rightNow = DateTime.local({ zone: topLevelInfo.user.timezone });
  const today = rightNow.toISODate();

  const bigScreenTabs = loaderData.homeConfig.tabs.filter(
    (t) => t.target === HomeTabTarget.BIG_SCREEN,
  );
  const smallScreenTabs = loaderData.homeConfig.tabs.filter(
    (t) => t.target === HomeTabTarget.SMALL_SCREEN,
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

  const widgetProps: WidgetProps = {
    rightNow,
    today,
    timezone: topLevelInfo.user.timezone,
    topLevelInfo,
    motd: loaderData.motd,
    habitTasks: {
      habits: loaderData.keyHabitResults.map((h) => h.habit),
      habitInboxTasks: sortedHabitInboxTasks,
      habitEntriesByRefId,
      optimisticUpdates,
      onCardMarkDone: handleCardMarkDone,
      onCardMarkNotDone: handleCardMarkNotDone,
    },
    habitStreak: {
      year: loaderData.keyHabitResults[0]?.streakMarkYear ?? rightNow.year,
      currentYear: rightNow.year,
      entries: loaderData.keyHabitResults,
      getYearUrl: (year) =>
        `/app/workspace?${newURLParams(query, "includeStreakMarksForYear", year.toString())}`,
    },
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
  bigScreenTabs: HomeTab[];
  widgetByRefId: Map<string, HomeWidget>;
  widgetProps: WidgetProps;
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
  smallScreenTabs: HomeTab[];
  widgetByRefId: Map<string, HomeWidget>;
  widgetProps: WidgetProps;
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
  widgetProps: WidgetProps;
}

function ActualWidget({ widget, widgetProps }: ActualWidgetProps) {
  switch (widget.the_type) {
    case WidgetType.MOTD:
      return <MOTDWidget {...widgetProps} />;
    case WidgetType.WORKING_MEM:
      return <div>Not implemented</div>;
    case WidgetType.KEY_HABITS_STREAKS:
      return <HabitKeyHabitStreakWidget {...widgetProps} />;
    case WidgetType.HABIT_INBOX_TASKS:
      return <HabitInboxTasksWidget {...widgetProps} />;
    case WidgetType.CALENDAR_DAY:
      return <CalendarDailyWidget {...widgetProps} />;
    case WidgetType.TIME_PLAN_VIEW:
      return <TimePlanViewWidget {...widgetProps} />;
    default:
      return <div>Not implemented</div>;
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

import { json, LoaderFunctionArgs } from "@remix-run/node";
import {
  Outlet,
  useFetcher,
  useNavigation,
  useSearchParams,
  type ShouldRevalidateFunction,
} from "@remix-run/react";
import Grid from "@mui/material/Grid2";
import {
  InboxTask,
  InboxTaskSource,
  InboxTaskStatus,
  RecurringTaskPeriod,
} from "@jupiter/webapi-client";
import { useContext, useState } from "react";
import { DateTime } from "luxon";
import { AnimatePresence } from "framer-motion";
import TuneIcon from "@mui/icons-material/Tune";
import { z } from "zod";
import { parseQuery } from "zodix";
import { Tabs, Tab , Stack } from "@mui/material";

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

enum MobileTab {
  FIRST = "First",
  HABIT_INBOX_TASKS = "Habit Tasks",
  CALENDAR = "Calendar",
  TIME_PLAN = "Time Plan",
}

export const handle = {
  displayType: DisplayType.TRUNK,
};

const QuerySchema = z.object({
  includeStreakMarksForYear: z
    .string()
    .transform((s) => parseInt(s, 10))
    .optional(),
});

export async function loader({ request }: LoaderFunctionArgs) {
  const query = parseQuery(request, QuerySchema);
  const rightNow = DateTime.now().toISODate();

  const apiClient = await getLoggedInApiClient(request);

  const homeConfigResponse = await apiClient.home.homeConfigLoad({});

  const motdResponse = await apiClient.motd.motdGetForToday({});
  const habitInboxTasksResponse = await apiClient.inboxTasks.inboxTaskFind({
    allow_archived: false,
    include_notes: false,
    include_time_event_blocks: false,
    filter_sources: [InboxTaskSource.HABIT],
  });

  let keyHabit1Response = undefined;
  if (homeConfigResponse.home_config.key_habits.length > 0) {
    keyHabit1Response = await apiClient.habits.habitLoad({
      ref_id: homeConfigResponse.home_config.key_habits[0],
      allow_archived: false,
      include_streak_marks_for_year: query.includeStreakMarksForYear,
    });
  }

  let keyHabit2Response = undefined;
  if (homeConfigResponse.home_config.key_habits.length > 1) {
    keyHabit2Response = await apiClient.habits.habitLoad({
      ref_id: homeConfigResponse.home_config.key_habits[1],
      allow_archived: false,
      include_streak_marks_for_year: query.includeStreakMarksForYear,
    });
  }

  let keyHabit3Response = undefined;
  if (homeConfigResponse.home_config.key_habits.length > 2) {
    keyHabit3Response = await apiClient.habits.habitLoad({
      ref_id: homeConfigResponse.home_config.key_habits[2],
      allow_archived: false,
      include_streak_marks_for_year: query.includeStreakMarksForYear,
    });
  }

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
    motd: motdResponse.motd,
    habitInboxTasks: habitInboxTasksResponse.entries,
    keyHabit1: keyHabit1Response,
    keyHabit2: keyHabit2Response,
    keyHabit3: keyHabit3Response,
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

  const [mobileTab, setMobileTab] = useState<MobileTab>(MobileTab.FIRST);

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

  const keyHabitEntries = [];
  if (loaderData.keyHabit1) {
    keyHabitEntries.push({
      habit: loaderData.keyHabit1?.habit,
      streakMarks: loaderData.keyHabit1?.streak_marks,
      inboxTasks: loaderData.keyHabit1?.inbox_tasks,
    });
  }
  if (loaderData.keyHabit2) {
    keyHabitEntries.push({
      habit: loaderData.keyHabit2?.habit,
      streakMarks: loaderData.keyHabit2?.streak_marks,
      inboxTasks: loaderData.keyHabit2?.inbox_tasks,
    });
  }
  if (loaderData.keyHabit3) {
    keyHabitEntries.push({
      habit: loaderData.keyHabit3?.habit,
      streakMarks: loaderData.keyHabit3?.streak_marks,
      inboxTasks: loaderData.keyHabit3?.inbox_tasks,
    });
  }

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
            <Grid container spacing={2}>
              <Grid size={{ md: 4 }}>
                <MOTDWidget motd={loaderData.motd} />
              </Grid>
              <Grid size={{ md: 4 }}>
                <HabitKeyHabitStreakWidget
                  year={loaderData.keyHabit1?.streak_mark_year ?? rightNow.year}
                  currentYear={rightNow.year}
                  entries={keyHabitEntries}
                  getYearUrl={(year) =>
                    `/app/workspace?${newURLParams(
                      query,
                      "includeStreakMarksForYear",
                      year.toString(),
                    )}`
                  }
                />
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid size={{ md: 4 }}>
                <HabitInboxTasksWidget
                  today={rightNow}
                  topLevelInfo={topLevelInfo}
                  habitInboxTasks={sortedHabitInboxTasks}
                  optimisticUpdates={optimisticUpdates}
                  habitEntriesByRefId={habitEntriesByRefId}
                  onCardMarkDone={handleCardMarkDone}
                  onCardMarkNotDone={handleCardMarkNotDone}
                />
              </Grid>
              <Grid size={{ md: 4 }}>
                <CalendarDailyWidget
                  rightNow={rightNow}
                  today={today}
                  timezone={topLevelInfo.user.timezone}
                  period={RecurringTaskPeriod.DAILY}
                  periodStartDate={today}
                  periodEndDate={today}
                  entries={loaderData.calendarEntriesForToday!}
                />
              </Grid>

              <Grid size={{ md: 4 }}>
                <TimePlanViewWidget
                  today={rightNow}
                  topLevelInfo={topLevelInfo}
                  timePlanForToday={loaderData.timePlanForToday}
                  timePlanForWeek={loaderData.timePlanForWeek}
                />
              </Grid>
            </Grid>
          </>
        )}

        {!isBigScreen && (
          <Stack>
            <Tabs
              value={mobileTab}
              onChange={(_, value) => setMobileTab(value)}
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab
                icon={<p>🏠</p>}
                iconPosition="top"
                label={MobileTab.FIRST}
                value={MobileTab.FIRST}
              />
              <Tab
                icon={<p>💪</p>}
                iconPosition="top"
                label={MobileTab.HABIT_INBOX_TASKS}
                value={MobileTab.HABIT_INBOX_TASKS}
              />
              <Tab
                icon={<p>📅</p>}
                iconPosition="top"
                label={MobileTab.CALENDAR}
                value={MobileTab.CALENDAR}
              />
              <Tab
                icon={<p>🏭</p>}
                iconPosition="top"
                label={MobileTab.TIME_PLAN}
                value={MobileTab.TIME_PLAN}
              />
            </Tabs>

            {mobileTab === MobileTab.FIRST && (
              <>
                <MOTDWidget motd={loaderData.motd} />

                <HabitKeyHabitStreakWidget
                  year={loaderData.keyHabit1?.streak_mark_year ?? rightNow.year}
                  currentYear={rightNow.year}
                  entries={keyHabitEntries}
                  getYearUrl={(year) =>
                    `/app/workspace?${newURLParams(
                      query,
                      "includeStreakMarksForYear",
                      year.toString(),
                    )}`
                  }
                />
              </>
            )}

            {mobileTab === MobileTab.HABIT_INBOX_TASKS && (
              <HabitInboxTasksWidget
                today={rightNow}
                topLevelInfo={topLevelInfo}
                habitInboxTasks={sortedHabitInboxTasks}
                optimisticUpdates={optimisticUpdates}
                habitEntriesByRefId={habitEntriesByRefId}
                onCardMarkDone={handleCardMarkDone}
                onCardMarkNotDone={handleCardMarkNotDone}
              />
            )}

            {mobileTab === MobileTab.CALENDAR && (
              <CalendarDailyWidget
                rightNow={rightNow}
                today={today}
                timezone={topLevelInfo.user.timezone}
                period={RecurringTaskPeriod.DAILY}
                periodStartDate={today}
                periodEndDate={today}
                entries={loaderData.calendarEntriesForToday!}
              />
            )}

            {mobileTab === MobileTab.TIME_PLAN && (
              <TimePlanViewWidget
                today={rightNow}
                topLevelInfo={topLevelInfo}
                timePlanForToday={loaderData.timePlanForToday}
                timePlanForWeek={loaderData.timePlanForWeek}
              />
            )}
          </Stack>
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

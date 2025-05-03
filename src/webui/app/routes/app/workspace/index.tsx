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
  TimePlan,
  TimePlanActivityDoneness,
  TimePlanActivity,
  BigPlan,
  TimePlanActivityFeasability,
  TimePlanActivityKind,
} from "@jupiter/webapi-client";
import { useContext, useState } from "react";
import { DateTime } from "luxon";
import { Stack } from "@mui/material";
import { AnimatePresence } from "framer-motion";
import TuneIcon from "@mui/icons-material/Tune";

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
import { MOTDCard } from "~/components/domain/concept/motd/motd-card";
import {
  filterInboxTasksForDisplay,
  inboxTaskFindEntryToParent,
  InboxTaskOptimisticState,
  InboxTaskParent,
  sortInboxTasksByEisenAndDifficulty,
  sortInboxTasksNaturally,
} from "~/logic/domain/inbox-task";
import { TopLevelInfo, TopLevelInfoContext } from "~/top-level-context";
import { InboxTaskStack } from "~/components/domain/concept/inbox-task/inbox-task-stack";
import {
  ActionableTime,
  actionableTimeToDateTime,
} from "~/rendering/actionable-time";
import { InboxTasksNoTasksCard } from "~/components/domain/concept/inbox-task/inbox-tasks-no-tasks-card";
import { ViewAsCalendarDaily } from "~/components/domain/application/calendar/view-as-calendar-daily";
import { DocsHelpSubject } from "~/components/infra/docs-help";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";
import { filterActivityByFeasabilityWithParents } from "~/logic/domain/time-plan-activity";
import { TimePlanMergedActivities } from "~/components/domain/concept/time-plan/time-plan-merged-activities";
import { NavSingle, SectionActions } from "~/components/infra/section-actions";
import { HabitStreakCalendar } from "~/components/domain/concept/habit/habit-streak-calendar";
import { newURLParams } from "~/logic/domain/navigation";
import { z } from "zod";
import { parseQuery } from "zodix";
import { StandardDivider } from "~/components/infra/standard-divider";
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
        <MOTDCard motd={loaderData.motd} />

        <Grid container spacing={2}>
        {loaderData.keyHabit1 && (
            <Grid size={{ md: 4 }}>
              <StandardDivider title={loaderData.keyHabit1.habit.name} size="small" />
              <HabitStreakCalendar
                year={loaderData.keyHabit1.streak_mark_year}
                currentYear={rightNow.year}
                habit={loaderData.keyHabit1.habit}
                streakMarks={loaderData.keyHabit1.streak_marks}
                inboxTasks={loaderData.keyHabit1.inbox_tasks}
                getYearUrl={(year) =>
                  `/app/workspace?${newURLParams(
                    query,
                    "includeStreakMarksForYear",
                    year.toString(),
                  )}`
                }
              />
            </Grid>
          )}
          {loaderData.keyHabit2 && (
            <Grid size={{ md: 4 }}>
              <StandardDivider title={loaderData.keyHabit2.habit.name} size="small" />
              <HabitStreakCalendar
                year={loaderData.keyHabit2.streak_mark_year}
                currentYear={rightNow.year}
                habit={loaderData.keyHabit2.habit}
                streakMarks={loaderData.keyHabit2.streak_marks}
                inboxTasks={loaderData.keyHabit2.inbox_tasks}
                getYearUrl={(year) =>
                  `/app/workspace?${newURLParams(
                    query,
                    "includeStreakMarksForYear",
                    year.toString(),
                  )}`
                }
              />
            </Grid>
          )}
          {loaderData.keyHabit3 && (
            <Grid size={{ md: 4 }}>
              <StandardDivider title={loaderData.keyHabit3.habit.name} size="small" />
              <HabitStreakCalendar
                year={loaderData.keyHabit3.streak_mark_year}
                currentYear={rightNow.year}
                habit={loaderData.keyHabit3.habit}
                streakMarks={loaderData.keyHabit3.streak_marks}
                inboxTasks={loaderData.keyHabit3.inbox_tasks}
                getYearUrl={(year) =>
                  `/app/workspace?${newURLParams(
                    query,
                    "includeStreakMarksForYear",
                    year.toString(),
                  )}`
                }
              />
            </Grid>
          )}
        </Grid>
        <Grid container spacing={2}>
          <Grid size={{ md: 4 }}>
            <HabitInboxTasks
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
            <ViewAsCalendarDaily
              rightNow={rightNow}
              today={today}
              timezone={topLevelInfo.user.timezone}
              period={RecurringTaskPeriod.DAILY}
              periodStartDate={today}
              periodEndDate={today}
              entries={loaderData.calendarEntriesForToday!}
              calendarLocation={""}
              isAdding={false}
            />
          </Grid>

          <Grid size={{ md: 4 }}>
            <TimePlans
              today={rightNow}
              topLevelInfo={topLevelInfo}
              timePlanForToday={loaderData.timePlanForToday}
              timePlanForWeek={loaderData.timePlanForWeek}
            />
          </Grid>
        </Grid>
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

interface HabitInboxTasksProps {
  today: DateTime;
  topLevelInfo: TopLevelInfo;
  habitInboxTasks: Array<InboxTask>;
  optimisticUpdates: { [key: string]: InboxTaskOptimisticState };
  habitEntriesByRefId: { [key: string]: InboxTaskParent };
  onCardMarkDone: (it: InboxTask) => void;
  onCardMarkNotDone: (it: InboxTask) => void;
}

function HabitInboxTasks(props: HabitInboxTasksProps) {
  const endOfTheWeek = props.today.endOf("week").endOf("day");
  const actionableTime = actionableTimeToDateTime(
    ActionableTime.ONE_WEEK,
    props.topLevelInfo.user.timezone,
  );

  const sortedInboxTasks = sortInboxTasksByEisenAndDifficulty(
    props.habitInboxTasks,
  );

  const inboxTasksForHabitsDueToday = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.habitEntriesByRefId,
    props.optimisticUpdates,
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
      dueDateEnd: props.today,
      allowPeriodsIfHabit: [RecurringTaskPeriod.DAILY],
    },
  );

  const inboxTasksForHabitsDueThisWeek = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.habitEntriesByRefId,
    props.optimisticUpdates,
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
      dueDateEnd: endOfTheWeek,
      allowPeriodsIfHabit: [RecurringTaskPeriod.WEEKLY],
    },
  );

  const habitsStack = (
    <Stack>
      <AnimatePresence>
        <InboxTaskStack
          key="habit-due-today"
          today={props.today}
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
          label="Due Today"
          inboxTasks={inboxTasksForHabitsDueToday}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.habitEntriesByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />

        <InboxTaskStack
          today={props.today}
          topLevelInfo={props.topLevelInfo}
          key="habit-due-this-week"
          showOptions={{
            showStatus: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due This Week"
          inboxTasks={inboxTasksForHabitsDueThisWeek}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.habitEntriesByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </AnimatePresence>
    </Stack>
  );

  if (
    inboxTasksForHabitsDueToday.length === 0 &&
    inboxTasksForHabitsDueThisWeek.length === 0
  ) {
    return (
      <InboxTasksNoTasksCard
        parent="habit"
        parentLabel="New Habit"
        parentNewLocations="/app/workspace/habits/new"
      />
    );
  }

  return habitsStack;
}

interface TimePlansProps {
  today: DateTime;
  topLevelInfo: TopLevelInfo;
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
}

function TimePlans(props: TimePlansProps) {
  if (!props.timePlanForToday && !props.timePlanForWeek) {
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
      {props.timePlanForToday && (
        <SingleTimePlan
          timePlan={props.timePlanForToday.timePlan}
          activities={props.timePlanForToday.activities}
          targetInboxTasks={props.timePlanForToday.targetInboxTasks}
          targetBigPlans={props.timePlanForToday.targetBigPlans}
          activityDoneness={props.timePlanForToday.activityDoneness}
        />
      )}
      {props.timePlanForWeek && (
        <SingleTimePlan
          timePlan={props.timePlanForWeek.timePlan}
          activities={props.timePlanForWeek.activities}
          targetInboxTasks={props.timePlanForWeek.targetInboxTasks}
          targetBigPlans={props.timePlanForWeek.targetBigPlans}
          activityDoneness={props.timePlanForWeek.activityDoneness}
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

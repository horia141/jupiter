import type {
  ADate,
  CalendarEventsEntries,
  CalendarEventsStats,
  CalendarEventsStatsPerSubperiod,
  EntityId,
  InboxTaskEntry,
  PersonEntry,
  ScheduleFullDaysEventEntry,
  ScheduleInDayEventEntry,
  TimeEventFullDaysBlock,
  TimeEventInDayBlock,
  Timezone,
} from "@jupiter/webapi-client";
import {
  RecurringTaskPeriod,
  TimeEventNamespace,
} from "@jupiter/webapi-client";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import {
  Box,
  Button,
  Paper,
  styled,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Typography,
  useTheme,
} from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  Outlet,
  useLocation,
  useSearchParams,
  useTransition,
} from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { DateTime } from "luxon";
import type { PropsWithChildren } from "react";
import React, { useContext, useEffect, useRef, useState } from "react";
import { z } from "zod";
import { parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityLink } from "~/components/infra/entity-card";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import {
  NavMultipleCompact,
  NavMultipleSpread,
  NavSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { aDateToDate, allDaysBetween } from "~/logic/domain/adate";
import { periodName } from "~/logic/domain/period";
import {
  scheduleStreamColorContrastingHex,
  scheduleStreamColorHex,
} from "~/logic/domain/schedule-stream-color";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowBranch,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";
import { measureText } from "~/utils";

enum View {
  CALENDAR = "calendar",
  SCHEDULE = "schedule",
}

export const handle = {
  displayType: DisplayType.TRUNK,
};

const QuerySchema = {
  today: z
    .string()
    .regex(/[0-9][0-9][0-9][0-9][-][0-9][0-9][-][0-9][0-9]/)
    .optional(),
  period: z.nativeEnum(RecurringTaskPeriod).optional(),
  view: z.nativeEnum(View).optional(),
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const query = parseQuery(request, QuerySchema);

  if (
    query.today === undefined ||
    query.period === undefined ||
    query.view === undefined
  ) {
    const today = DateTime.now().toISODate();
    const period = RecurringTaskPeriod.WEEKLY;
    return redirect(
      `${request.url}?today=${today}&period=${period}&view=${View.CALENDAR}`
    );
  }

  const response = await getLoggedInApiClient(
    session
  ).calendar.calendarLoadForDateAndPeriod({
    right_now: query.today,
    period: query.period,
    stats_subperiod: statsSubperiodForPeriod(query.period),
  });

  return json({
    today: query.today as string,
    period: query.period as RecurringTaskPeriod,
    view: query.view as View,
    periodStartDate: response.period_start_date,
    periodEndDate: response.period_end_date,
    prevPeriodStartDate: response.prev_period_start_date,
    nextPeriodStartDate: response.next_period_start_date,
    entries: response.entries || undefined,
    stats: response.stats || undefined,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function CalendarView() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const transition = useTransition();
  const location = useLocation();
  const [query] = useSearchParams();

  const calendarLocation = location.pathname.replace(
    /\/workspace\/calendar/,
    ""
  );

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = transition.state === "idle";

  const shouldShowABranch = useTrunkNeedsToShowBranch();
  const shouldShowALeafToo = useTrunkNeedsToShowLeaf();

  const theRealToday = DateTime.now().toISODate() as ADate;

  return (
    <TrunkPanel
      key="calendar"
      createLocation={`/workspace/calendar/schedule/event-in-day/new?${query}`}
      fixedScrollRestaurationTo={320} // About 5am
      actions={
        <SectionActions
          id="calendar"
          topLevelInfo={topLevelInfo}
          inputsEnabled={inputsEnabled}
          actions={[
            NavMultipleCompact({
              navs: [
                NavSingle({
                  text: "New Event In Day",
                  link: `/workspace/calendar/schedule/event-in-day/new?${query}`,
                }),
                NavSingle({
                  text: "New Event Full Days",
                  link: `/workspace/calendar/schedule/event-full-days/new?${query}`,
                }),
                NavSingle({
                  text: "New Calendar Stream",
                  link: `/workspace/calendar/schedule/stream/new?${query}`,
                }),
                NavSingle({
                  text: "View Calendar Streams",
                  link: `/workspace/calendar/schedule/stream?${query}`,
                }),
              ],
            }),
            NavMultipleSpread({
              navs: [
                NavSingle({
                  text: "Today",
                  link: `/workspace/calendar${calendarLocation}?today=${theRealToday}&period=${loaderData.period}&view=${loaderData.view}`,
                }),
                NavSingle({
                  text: "Prev",
                  icon: <ArrowBackIcon />,
                  link: `/workspace/calendar${calendarLocation}?today=${loaderData.prevPeriodStartDate}&period=${loaderData.period}&view=${loaderData.view}`,
                }),
                NavSingle({
                  text: "Next",
                  icon: <ArrowForwardIcon />,
                  link: `/workspace/calendar${calendarLocation}?today=${loaderData.nextPeriodStartDate}&period=${loaderData.period}&view=${loaderData.view}`,
                }),
              ],
            }),
            NavMultipleCompact({
              navs: [
                NavSingle({
                  text: periodName(RecurringTaskPeriod.DAILY),
                  highlight: loaderData.period === RecurringTaskPeriod.DAILY,
                  link: `/workspace/calendar${calendarLocation}?today=${loaderData.today}&period=${RecurringTaskPeriod.DAILY}&view=${loaderData.view}`,
                }),
                NavSingle({
                  text: periodName(RecurringTaskPeriod.WEEKLY),
                  highlight: loaderData.period === RecurringTaskPeriod.WEEKLY,
                  link: `/workspace/calendar${calendarLocation}?today=${loaderData.today}&period=${RecurringTaskPeriod.WEEKLY}&view=${loaderData.view}`,
                }),
                NavSingle({
                  text: periodName(RecurringTaskPeriod.MONTHLY),
                  highlight: loaderData.period === RecurringTaskPeriod.MONTHLY,
                  link: `/workspace/calendar${calendarLocation}?today=${loaderData.today}&period=${RecurringTaskPeriod.MONTHLY}&view=${loaderData.view}`,
                }),
                NavSingle({
                  text: periodName(RecurringTaskPeriod.QUARTERLY),
                  highlight:
                    loaderData.period === RecurringTaskPeriod.QUARTERLY,
                  link: `/workspace/calendar${calendarLocation}?today=${loaderData.today}&period=${RecurringTaskPeriod.QUARTERLY}&view=${loaderData.view}`,
                }),
                NavSingle({
                  text: periodName(RecurringTaskPeriod.YEARLY),
                  highlight: loaderData.period === RecurringTaskPeriod.YEARLY,
                  link: `/workspace/calendar${calendarLocation}?today=${loaderData.today}&period=${RecurringTaskPeriod.YEARLY}&view=${loaderData.view}`,
                }),
              ],
            }),
            NavMultipleSpread({
              navs: [
                NavSingle({
                  text: "Calendar",
                  link: `/workspace/calendar${calendarLocation}?today=${loaderData.today}&period=${loaderData.period}&view=${View.CALENDAR}`,
                  highlight: loaderData.view === View.CALENDAR,
                }),
                NavSingle({
                  text: "Schedule",
                  link: `/workspace/calendar${calendarLocation}?today=${loaderData.today}&period=${loaderData.period}&&view=${View.SCHEDULE}`,
                  highlight: loaderData.view === View.SCHEDULE,
                }),
              ],
            }),
          ]}
        />
      }
      returnLocation="/workspace"
    >
      <NestingAwareBlock
        branchForceHide={shouldShowABranch}
        shouldHide={shouldShowABranch || shouldShowALeafToo}
      >
        {loaderData.view === View.CALENDAR &&
          loaderData.period === RecurringTaskPeriod.DAILY && (
            <ViewAsCalendarDaily
              timezone={topLevelInfo.user.timezone}
              today={theRealToday}
              periodStartDate={loaderData.periodStartDate}
              periodEndDate={loaderData.periodEndDate}
              entries={loaderData.entries}
              stats={loaderData.stats}
              calendarLocation={calendarLocation}
            />
          )}

        {loaderData.view === View.CALENDAR &&
          loaderData.period === RecurringTaskPeriod.WEEKLY && (
            <ViewAsCalendarWeekly
              timezone={topLevelInfo.user.timezone}
              today={theRealToday}
              periodStartDate={loaderData.periodStartDate}
              periodEndDate={loaderData.periodEndDate}
              entries={loaderData.entries}
              stats={loaderData.stats}
              calendarLocation={calendarLocation}
            />
          )}

        {loaderData.view === View.CALENDAR &&
          loaderData.period === RecurringTaskPeriod.MONTHLY && (
            <ViewAsCalendarMonthly
              timezone={topLevelInfo.user.timezone}
              today={theRealToday}
              periodStartDate={loaderData.periodStartDate}
              periodEndDate={loaderData.periodEndDate}
              entries={loaderData.entries}
              stats={loaderData.stats}
              calendarLocation={calendarLocation}
            />
          )}

        {loaderData.view === View.CALENDAR &&
          loaderData.period === RecurringTaskPeriod.QUARTERLY && (
            <ViewAsCalendarQuarterly
              timezone={topLevelInfo.user.timezone}
              today={theRealToday}
              periodStartDate={loaderData.periodStartDate}
              periodEndDate={loaderData.periodEndDate}
              entries={loaderData.entries}
              stats={loaderData.stats}
              calendarLocation={calendarLocation}
            />
          )}

        {loaderData.view === View.CALENDAR &&
          loaderData.period === RecurringTaskPeriod.YEARLY && (
            <ViewAsCalendarYearly
              timezone={topLevelInfo.user.timezone}
              today={theRealToday}
              periodStartDate={loaderData.periodStartDate}
              periodEndDate={loaderData.periodEndDate}
              entries={loaderData.entries}
              stats={loaderData.stats}
              calendarLocation={calendarLocation}
            />
          )}

        {loaderData.view === View.SCHEDULE &&
          (loaderData.period === RecurringTaskPeriod.DAILY ||
            loaderData.period === RecurringTaskPeriod.WEEKLY) && (
            <ViewAsScheduleDailyAndWeekly
              timezone={topLevelInfo.user.timezone}
              today={theRealToday}
              periodStartDate={loaderData.periodStartDate}
              periodEndDate={loaderData.periodEndDate}
              entries={loaderData.entries}
              stats={loaderData.stats}
              calendarLocation={calendarLocation}
            />
          )}

        {loaderData.view === View.SCHEDULE &&
          (loaderData.period === RecurringTaskPeriod.MONTHLY ||
            loaderData.period === RecurringTaskPeriod.QUARTERLY ||
            loaderData.period === RecurringTaskPeriod.YEARLY) && (
            <ViewAsScheduleMonthlyQuarterlyAndYearly
              timezone={topLevelInfo.user.timezone}
              today={theRealToday}
              periodStartDate={loaderData.periodStartDate}
              periodEndDate={loaderData.periodEndDate}
              entries={loaderData.entries}
              stats={loaderData.stats}
              calendarLocation={calendarLocation}
            />
          )}
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the calendar events! Please try again!`
);

const MAX_VISIBLE_TIME_EVENT_FULL_DAYS = 3;

interface ViewAsProps {
  today: ADate;
  timezone: Timezone;
  periodStartDate: ADate;
  periodEndDate: ADate;
  entries?: CalendarEventsEntries;
  stats?: CalendarEventsStats;
  calendarLocation: string;
}

function ViewAsCalendarDaily(props: ViewAsProps) {
  const isBigScreen = useBigScreen();

  const [showAllTimeEventFullDays, setShowAllTimeEventFullDays] =
    useState(false);

  if (props.entries === undefined) {
    throw new Error("Entries are required");
  }

  const combinedTimeEventFullDays: Array<CombinedTimeEventFullDaysEntry> = [];
  for (const entry of props.entries.schedule_event_full_days_entries) {
    combinedTimeEventFullDays.push({
      time_event: entry.time_event,
      entry: entry,
    });
  }
  for (const entry of props.entries.person_entries) {
    combinedTimeEventFullDays.push({
      time_event: entry.birthday_time_event,
      entry: entry,
    });
  }

  const combinedTimeEventInDay: Array<CombinedTimeEventInDayEntry> = [];
  for (const entry of props.entries.schedule_event_in_day_entries) {
    combinedTimeEventInDay.push({
      time_event: entry.time_event,
      entry: entry,
    });
  }
  for (const entry of props.entries.inbox_task_entries) {
    for (const timeEvent of entry.time_events) {
      combinedTimeEventInDay.push({
        time_event: timeEvent,
        entry: entry,
      });
    }
  }

  const partitionedCombinedTimeEventFullDays =
    combinedTimeEventFullDayEntryPartionByDay(combinedTimeEventFullDays);
  const thePartititionFullDays =
    partitionedCombinedTimeEventFullDays[props.periodStartDate] || [];
  const partitionedCombinedTimeEventInDay =
    combinedTimeEventInDayEntryPartionByDay(
      combinedTimeEventInDay,
      props.timezone
    );
  const thePartitionInDay =
    partitionedCombinedTimeEventInDay[props.periodStartDate] || [];

  const startOfDay = DateTime.fromISO(`${props.periodStartDate}T00:00:00`, {
    zone: props.timezone,
  });

  const rightNow = DateTime.now().setZone(props.timezone);

  return (
    <Box
      sx={{
        position: "relative",
        margin: isBigScreen ? "auto" : "initial",
        width: isBigScreen ? "300px" : "100%",
        paddingTop:
          isBigScreen || thePartititionFullDays.length > 0 ? "0" : "1rem",
      }}
    >
      <ViewAsCalendarDaysAndFullDaysContiner>
        <Box sx={{ display: "flex", flexDirection: "row", gap: "0.5rem" }}>
          <ViewAsCalendarEmptyCell />
          <ViewAsCalendarDateHeader
            today={props.today}
            date={props.periodStartDate}
          />
          <ViewAsCalendarEmptyCell />
        </Box>

        <Box sx={{ display: "flex", flexDirection: "row" }}>
          {thePartititionFullDays.length > MAX_VISIBLE_TIME_EVENT_FULL_DAYS && (
            <ViewAsCalendarMoreButton
              showAllTimeEventFullDays={showAllTimeEventFullDays}
              setShowAllTimeEventFullDays={setShowAllTimeEventFullDays}
            />
          )}
          {thePartititionFullDays.length <=
            MAX_VISIBLE_TIME_EVENT_FULL_DAYS && <ViewAsCalendarEmptyCell />}

          <ViewAsCalendarTimeEventFullDaysColumn
            today={props.today}
            date={props.periodStartDate}
            timezone={props.timezone}
            showAll={showAllTimeEventFullDays}
            maxFullDaysEntriesCnt={thePartititionFullDays.length}
            timeEventFullDays={thePartititionFullDays}
          />

          <ViewAsCalendarEmptyCell />
        </Box>
      </ViewAsCalendarDaysAndFullDaysContiner>

      <ViewAsCalendarInDayContainer>
        <ViewAsCalendarLeftColumn startOfDay={startOfDay} />
        <ViewAsCalendarTimeEventInDayColumn
          today={props.today}
          rightNow={rightNow}
          date={props.periodStartDate}
          timezone={props.timezone}
          timeEventsInDay={thePartitionInDay}
        />
        <ViewAsCalendarRightColumn />
      </ViewAsCalendarInDayContainer>
    </Box>
  );
}

function ViewAsCalendarWeekly(props: ViewAsProps) {
  const isBigScreen = useBigScreen();

  const [showAllTimeEventFullDays, setShowAllTimeEventFullDays] =
    useState(false);

  if (props.entries === undefined) {
    throw new Error("Entries are required");
  }

  const combinedTimeEventFullDays: Array<CombinedTimeEventFullDaysEntry> = [];
  for (const entry of props.entries.schedule_event_full_days_entries) {
    combinedTimeEventFullDays.push({
      time_event: entry.time_event,
      entry: entry,
    });
  }
  for (const entry of props.entries.person_entries) {
    combinedTimeEventFullDays.push({
      time_event: entry.birthday_time_event,
      entry: entry,
    });
  }

  const combinedTimeEventInDay: Array<CombinedTimeEventInDayEntry> = [];
  for (const entry of props.entries.schedule_event_in_day_entries) {
    combinedTimeEventInDay.push({
      time_event: entry.time_event,
      entry: entry,
    });
  }
  for (const entry of props.entries.inbox_task_entries) {
    for (const timeEvent of entry.time_events) {
      combinedTimeEventInDay.push({
        time_event: timeEvent,
        entry: entry,
      });
    }
  }

  const partitionedCombinedTimeEventFullDays =
    combinedTimeEventFullDayEntryPartionByDay(combinedTimeEventFullDays);
  const partitionedCombinedTimeEventInDay =
    combinedTimeEventInDayEntryPartionByDay(
      combinedTimeEventInDay,
      props.timezone
    );

  const maxFullDaysEntriesCnt = Math.max(
    ...Object.values(partitionedCombinedTimeEventFullDays).map(
      (entries) => entries.length
    )
  );

  const startOfDay = DateTime.now().setZone(props.timezone).startOf("day");
  const rightNow = DateTime.now().setZone(props.timezone);
  const allDays = allDaysBetween(props.periodStartDate, props.periodEndDate);

  return (
    <Box
      sx={{
        position: "relative",
        width: "100%",
        margin: isBigScreen ? "auto" : "initial",
        paddingTop: isBigScreen || maxFullDaysEntriesCnt > 0 ? "0" : "1rem",
      }}
    >
      <ViewAsCalendarDaysAndFullDaysContiner>
        <Box sx={{ display: "flex", flexDirection: "row", gap: "0.1rem" }}>
          <ViewAsCalendarEmptyCell />
          {allDays.map((date, idx) => (
            <ViewAsCalendarDateHeader
              key={idx}
              today={props.today}
              date={date}
            />
          ))}
          <ViewAsCalendarEmptyCell />
        </Box>

        <Box sx={{ display: "flex", flexDirection: "row", gap: "0.1rem" }}>
          {maxFullDaysEntriesCnt > MAX_VISIBLE_TIME_EVENT_FULL_DAYS && (
            <ViewAsCalendarMoreButton
              showAllTimeEventFullDays={showAllTimeEventFullDays}
              setShowAllTimeEventFullDays={setShowAllTimeEventFullDays}
            />
          )}
          {maxFullDaysEntriesCnt <= MAX_VISIBLE_TIME_EVENT_FULL_DAYS && (
            <ViewAsCalendarEmptyCell />
          )}

          {allDays.map((date, idx) => (
            <ViewAsCalendarTimeEventFullDaysColumn
              key={idx}
              today={props.today}
              date={date}
              timezone={props.timezone}
              showAll={showAllTimeEventFullDays}
              maxFullDaysEntriesCnt={maxFullDaysEntriesCnt}
              timeEventFullDays={
                partitionedCombinedTimeEventFullDays[date] || []
              }
            />
          ))}

          <ViewAsCalendarEmptyCell />
        </Box>
      </ViewAsCalendarDaysAndFullDaysContiner>

      <ViewAsCalendarInDayContainer>
        <ViewAsCalendarLeftColumn startOfDay={startOfDay} />

        {allDays.map((date, idx) => (
          <ViewAsCalendarTimeEventInDayColumn
            key={idx}
            today={props.today}
            rightNow={rightNow}
            date={date}
            timezone={props.timezone}
            timeEventsInDay={partitionedCombinedTimeEventInDay[date] || []}
          />
        ))}

        <ViewAsCalendarRightColumn />
      </ViewAsCalendarInDayContainer>
    </Box>
  );
}

function ViewAsCalendarMonthly(props: ViewAsProps) {
  if (props.stats === undefined) {
    throw new Error("Stats are required");
  }

  const periodStartDate = DateTime.fromISO(props.periodStartDate);
  const periodEndDate = DateTime.fromISO(props.periodEndDate);
  const firstWeekIdx = periodStartDate.weekNumber;

  const weeks = [];
  for (
    let currWeek = periodStartDate.startOf("week");
    currWeek <= periodEndDate;
    currWeek = currWeek.plus({ weeks: 1 })
  ) {
    weeks.push(currWeek);
  }

  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns:
          "3rem [mon] 1fr [tue] 1fr [wed] 1fr [thu] 1fr [fri] 1fr [sat] 1fr [sun] 1fr",
        gridTemplateRows: "auto",
        gridGap: "0.25rem",
      }}
    >
      <Box sx={{ gridRowStart: 1, gridColumnStart: 1 }}>Week</Box>
      <Box sx={{ gridRowStart: 1, gridColumnStart: "mon" }}>Mon</Box>
      <Box sx={{ gridRowStart: 1, gridColumnStart: "tue" }}>Tue</Box>
      <Box sx={{ gridRowStart: 1, gridColumnStart: "wed" }}>Wed</Box>
      <Box sx={{ gridRowStart: 1, gridColumnStart: "thu" }}>Thu</Box>
      <Box sx={{ gridRowStart: 1, gridColumnStart: "fri" }}>Fri</Box>
      <Box sx={{ gridRowStart: 1, gridColumnStart: "sat" }}>Sat</Box>
      <Box sx={{ gridRowStart: 1, gridColumnStart: "sun" }}>Sun</Box>

      {weeks.map((week, idx) => {
        let gridRowStart = week.weekNumber - firstWeekIdx + 2;
        if (
          periodStartDate.month === 1 &&
          periodStartDate.startOf("week").weekNumber > 10
        ) {
          // We're starting the year, but the first week of the year
          // might be in the last year.
          gridRowStart = idx + 2;
        } else if (week.weekNumber < firstWeekIdx) {
          // We're at the end of the year, and the week number is 1 of
          // the next year.
          gridRowStart = Math.min(
            weeks.length + 1,
            week.weeksInWeekYear + 1 - firstWeekIdx + 2
          );
        }

        return (
          <Box
            key={idx}
            sx={{
              gridRowStart: gridRowStart,
              gridColumnStart: 1,
            }}
          >
            <ViewAsCalendarGoToCell
              label={`W${week.weekNumber}`}
              period={RecurringTaskPeriod.WEEKLY}
              periodStart={week.toISODate()}
              calendarLocation={props.calendarLocation}
            />
          </Box>
        );
      })}

      {props.stats.per_subperiod.map((stats, idx) => {
        const startDate = DateTime.fromISO(stats.period_start_date);

        let gridRowStart = startDate.weekNumber - firstWeekIdx + 2;
        if (
          periodStartDate.month === 1 &&
          periodStartDate.startOf("week").weekNumber > 10
        ) {
          // We're starting the year, but the first week of the year
          // might be in the last year.
          let lastDay = startDate.endOf("week").day;
          if (lastDay < startDate.day) {
            lastDay = startDate.daysInMonth + lastDay;
          }
          gridRowStart = Math.floor(lastDay / 7) + 2;
        } else if (startDate.weekNumber < firstWeekIdx) {
          // We're at the end of the year, and the week number is 1 of
          // the next year.
          gridRowStart = Math.min(
            weeks.length + 1,
            periodStartDate.weeksInWeekYear + 1 - firstWeekIdx + 2
          );
        }

        return (
          <Box
            key={idx}
            sx={{
              gridRowStart: gridRowStart,
              gridColumnStart: startDate.weekdayShort.toLowerCase(),
            }}
          >
            <ViewAsCalendarStatsCell
              label={startDate.day.toString()}
              forceColumn={false}
              showCompact={true}
              stats={stats}
              calendarLocation={props.calendarLocation}
            />
          </Box>
        );
      })}
    </Box>
  );
}

function ViewAsCalendarQuarterly(props: ViewAsProps) {
  if (props.stats === undefined) {
    throw new Error("Stats are required");
  }

  const periodStartDate = DateTime.fromISO(props.periodStartDate);
  const periodEndDate = DateTime.fromISO(props.periodEndDate);

  const months = [];
  for (
    let currMonth = periodStartDate;
    currMonth < periodEndDate;
    currMonth = currMonth.plus({ months: 1 })
  ) {
    months.push(currMonth);
  }

  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns:
          "3rem [w1] 1fr [w2] 1fr [w3] 1fr [w4] 1fr [w5] 1fr [w6] 1fr",
        gridTemplateRows: "auto",
        gridGap: "0.25rem",
      }}
    >
      <Box sx={{ gridRowStart: 1, gridColumnStart: 1 }}>Month</Box>

      <Box sx={{ gridRowStart: 1, gridColumnStart: "w1" }}>W1</Box>
      <Box sx={{ gridRowStart: 1, gridColumnStart: "w2" }}>W2</Box>
      <Box sx={{ gridRowStart: 1, gridColumnStart: "w3" }}>W3</Box>
      <Box sx={{ gridRowStart: 1, gridColumnStart: "w4" }}>W4</Box>
      <Box sx={{ gridRowStart: 1, gridColumnStart: "w5" }}>W5</Box>
      <Box sx={{ gridRowStart: 1, gridColumnStart: "w6" }}>W6</Box>

      {months.map((month, idx) => {
        return (
          <Box
            key={idx}
            sx={{
              gridRowStart: month.month - periodStartDate.month + 2,
              gridColumnStart: 1,
            }}
          >
            <ViewAsCalendarGoToCell
              label={month.monthShort}
              period={RecurringTaskPeriod.MONTHLY}
              periodStart={month.toISODate()}
              calendarLocation={props.calendarLocation}
            />
          </Box>
        );
      })}

      {props.stats.per_subperiod.map((stats, idx) => {
        const startDate = DateTime.fromISO(stats.period_start_date);
        const monthStartDate = startDate.startOf("month");

        if (
          periodStartDate.month === 10 &&
          startDate.weekNumber < periodStartDate.weekNumber
        ) {
          // Last weeks of the year tend to behave in a complex way
          // Checkout for more https://en.wikipedia.org/wiki/ISO_week_date.
          // It's simpler not to show them in this context, and just
          // let them appear in the next year.
          return null;
        }

        let gridColumnStart =
          startDate.weekNumber - monthStartDate.weekNumber + 1;
        if (monthStartDate.month === 1) {
          gridColumnStart = idx + 1;
        }

        return (
          <Box
            key={idx}
            sx={{
              gridRowStart: monthStartDate.month - periodStartDate.month + 2,
              gridColumnStart: `w${gridColumnStart}`,
            }}
          >
            <ViewAsCalendarStatsCell
              label={`Week ${startDate.weekNumber}`}
              forceColumn={false}
              showCompact={true}
              stats={stats}
              calendarLocation={props.calendarLocation}
            />
          </Box>
        );
      })}
    </Box>
  );
}

function ViewAsCalendarYearly(props: ViewAsProps) {
  const isBigScreen = useBigScreen();

  if (props.stats === undefined) {
    throw new Error("Stats are required");
  }

  const periodStartDate = DateTime.fromISO(props.periodStartDate);

  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns: "3rem 1fr 1fr 1fr",
        gridTemplateRows: "min-content min-content min-content min-content",
        gridGap: "0.25rem",
      }}
    >
      <Box sx={{ gridRowStart: 1, gridColumnStart: 1 }}>
        <ViewAsCalendarGoToCell
          label="Q1"
          period={RecurringTaskPeriod.QUARTERLY}
          periodStart={`${periodStartDate.year}-01-01`}
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 1, gridColumnStart: 2 }}>
        <ViewAsCalendarStatsCell
          label="Jan"
          forceColumn={isBigScreen}
          showCompact={!isBigScreen}
          stats={
            props.stats.per_subperiod.find(
              (s) => s.period_start_date === `${periodStartDate.year}-01-01`
            )!
          }
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 1, gridColumnStart: 3 }}>
        <ViewAsCalendarStatsCell
          label="Feb"
          forceColumn={isBigScreen}
          showCompact={!isBigScreen}
          stats={
            props.stats.per_subperiod.find(
              (s) => s.period_start_date === `${periodStartDate.year}-02-01`
            )!
          }
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 1, gridColumnStart: 4 }}>
        <ViewAsCalendarStatsCell
          label="Mar"
          forceColumn={isBigScreen}
          showCompact={!isBigScreen}
          stats={
            props.stats.per_subperiod.find(
              (s) => s.period_start_date === `${periodStartDate.year}-03-01`
            )!
          }
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 2, gridColumnStart: 1 }}>
        <ViewAsCalendarGoToCell
          label="Q2"
          period={RecurringTaskPeriod.QUARTERLY}
          periodStart={`${periodStartDate.year}-04-01`}
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 2, gridColumnStart: 2 }}>
        <ViewAsCalendarStatsCell
          label="Apr"
          forceColumn={isBigScreen}
          showCompact={!isBigScreen}
          stats={
            props.stats.per_subperiod.find(
              (s) => s.period_start_date === `${periodStartDate.year}-04-01`
            )!
          }
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 2, gridColumnStart: 3 }}>
        <ViewAsCalendarStatsCell
          label="May"
          forceColumn={isBigScreen}
          showCompact={!isBigScreen}
          stats={
            props.stats.per_subperiod.find(
              (s) => s.period_start_date === `${periodStartDate.year}-05-01`
            )!
          }
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 2, gridColumnStart: 4 }}>
        <ViewAsCalendarStatsCell
          label="Jun"
          forceColumn={isBigScreen}
          showCompact={!isBigScreen}
          stats={
            props.stats.per_subperiod.find(
              (s) => s.period_start_date === `${periodStartDate.year}-06-01`
            )!
          }
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 3, gridColumnStart: 1 }}>
        <ViewAsCalendarGoToCell
          label="Q3"
          period={RecurringTaskPeriod.QUARTERLY}
          periodStart={`${periodStartDate.year}-07-01`}
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 3, gridColumnStart: 2 }}>
        <ViewAsCalendarStatsCell
          label="Jul"
          forceColumn={isBigScreen}
          showCompact={!isBigScreen}
          stats={
            props.stats.per_subperiod.find(
              (s) => s.period_start_date === `${periodStartDate.year}-07-01`
            )!
          }
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 3, gridColumnStart: 3 }}>
        <ViewAsCalendarStatsCell
          label="Aug"
          forceColumn={isBigScreen}
          showCompact={!isBigScreen}
          stats={
            props.stats.per_subperiod.find(
              (s) => s.period_start_date === `${periodStartDate.year}-08-01`
            )!
          }
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 3, gridColumnStart: 4 }}>
        <ViewAsCalendarStatsCell
          label="Sep"
          forceColumn={isBigScreen}
          showCompact={!isBigScreen}
          stats={
            props.stats.per_subperiod.find(
              (s) => s.period_start_date === `${periodStartDate.year}-09-01`
            )!
          }
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 4, gridColumnStart: 1 }}>
        <ViewAsCalendarGoToCell
          label="Q4"
          period={RecurringTaskPeriod.QUARTERLY}
          periodStart={`${periodStartDate.year}-10-01`}
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 4, gridColumnStart: 2 }}>
        <ViewAsCalendarStatsCell
          label="Oct"
          forceColumn={isBigScreen}
          showCompact={!isBigScreen}
          stats={
            props.stats.per_subperiod.find(
              (s) => s.period_start_date === `${periodStartDate.year}-10-01`
            )!
          }
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 4, gridColumnStart: 3 }}>
        <ViewAsCalendarStatsCell
          label="Nov"
          forceColumn={isBigScreen}
          showCompact={!isBigScreen}
          stats={
            props.stats.per_subperiod.find(
              (s) => s.period_start_date === `${periodStartDate.year}-11-01`
            )!
          }
          calendarLocation={props.calendarLocation}
        />
      </Box>

      <Box sx={{ gridRowStart: 4, gridColumnStart: 4 }}>
        <ViewAsCalendarStatsCell
          label="Dec"
          forceColumn={isBigScreen}
          showCompact={!isBigScreen}
          stats={
            props.stats.per_subperiod.find(
              (s) => s.period_start_date === `${periodStartDate.year}-12-01`
            )!
          }
          calendarLocation={props.calendarLocation}
        />
      </Box>
    </Box>
  );
}

interface ViewAsCalendarDateHeaderProps {
  today: ADate;
  date: ADate;
}

function ViewAsCalendarDateHeader(props: ViewAsCalendarDateHeaderProps) {
  const theme = useTheme();
  const theDate = DateTime.fromISO(`${props.date}T00:00:00`);
  return (
    <Box
      sx={{
        minWidth: "7rem",
        flexGrow: "1",
        textAlign: "center",
      }}
    >
      <Box
        sx={{
          borderRadius: "50%",
          width: "50%",
          margin: "auto",
          backgroundColor:
            props.date === props.today
              ? theme.palette.info.light
              : "transparent",
        }}
      >
        <Typography sx={{ fontSize: "1.1em" }}>
          {theDate.toFormat("ccc")}
        </Typography>
        <Typography variant="h6">{theDate.toFormat("dd")}</Typography>
      </Box>
    </Box>
  );
}

interface ViewAsCalendarLeftColumnProps {
  startOfDay: DateTime;
}

function ViewAsCalendarLeftColumn(props: ViewAsCalendarLeftColumnProps) {
  const theme = useTheme();
  const hours = Array.from({ length: 24 }, (_, i) =>
    props.startOfDay.plus({ hours: i })
  );

  return (
    <Box
      sx={{
        width: "3.5rem",
        height: "96rem",
        position: "sticky",
        left: "0px",
        top: "0px",
        backgroundColor: theme.palette.background.paper,
        zIndex: theme.zIndex.appBar + 100,
        borderRight: "1px solid darkgray",
      }}
    >
      {hours.map((hour, idx) => (
        <Box
          key={idx}
          sx={{
            height: "4rem",
            width: "3.5rem",
            display: "flex",
            justifyContent: "center",
            alignItems: "top",
          }}
        >
          {hour.toFormat("HH:mm")}
        </Box>
      ))}
    </Box>
  );
}

function ViewAsCalendarRightColumn() {
  return (
    <Box
      sx={{
        width: "3.5rem",
        height: "96rem",
      }}
    ></Box>
  );
}

interface ViewAsCalendarTimeEventFullDaysColumnProps {
  today: ADate;
  date: ADate;
  timezone: Timezone;
  showAll: boolean;
  maxFullDaysEntriesCnt: number;
  timeEventFullDays: Array<CombinedTimeEventFullDaysEntry>;
}

function ViewAsCalendarTimeEventFullDaysColumn(
  props: ViewAsCalendarTimeEventFullDaysColumnProps
) {
  return (
    <Box sx={{ flex: 1 }}>
      {props.timeEventFullDays.map((entry, index) => {
        if (index >= MAX_VISIBLE_TIME_EVENT_FULL_DAYS && !props.showAll) {
          return null;
        }

        return (
          <ViewAsCalendarTimeEventFullDaysCell
            key={index}
            timezone={props.timezone}
            entry={entry}
          />
        );
      })}
    </Box>
  );
}

interface ViewAsCalendarTimeEventFullDaysCellProps {
  timezone: Timezone;
  entry: CombinedTimeEventFullDaysEntry;
}

function ViewAsCalendarTimeEventFullDaysCell(
  props: ViewAsCalendarTimeEventFullDaysCellProps
) {
  const [query] = useSearchParams();
  const containerRef = useRef<HTMLDivElement>(null);

  const [containerWidth, setContainerWidth] = useState(120);
  useEffect(() => {
    setContainerWidth(containerRef.current?.clientWidth || 120);
  }, [containerRef]);

  switch (props.entry.time_event.namespace) {
    case TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK:
      const fullDaysEntry = props.entry.entry as ScheduleFullDaysEventEntry;

      const clippedName = clipTimeEventFullDaysNameToWhatFits(
        fullDaysEntry.event.name,
        12,
        containerWidth - 32 // A hack of sorts
      );

      return (
        <Box
          ref={containerRef}
          sx={{
            minWidth: "7rem",
            fontSize: "12px",
            backgroundColor: scheduleStreamColorHex(fullDaysEntry.stream.color),
            borderRadius: "0.25rem",
            padding: "0.25rem",
            paddingLeft: "0.5rem",
            width: "100%",
            height: "2rem",
            marginBottom: "0.25rem",
            overflow: "hidden",
          }}
        >
          <EntityLink
            key={`schedule-event-full-days-${fullDaysEntry.event.ref_id}`}
            to={`/workspace/calendar/schedule/event-full-days/${fullDaysEntry.event.ref_id}?${query}`}
          >
            <EntityNameComponent
              name={clippedName}
              color={scheduleStreamColorContrastingHex(
                fullDaysEntry.stream.color
              )}
            />
          </EntityLink>
        </Box>
      );

    case TimeEventNamespace.PERSON_BIRTHDAY:
      throw new Error("Not implemented");

    default:
      throw new Error("Unexpected namespace");
  }
}

interface ViewAsCalendarTimeEventInDayColumnProps {
  today: ADate;
  rightNow: DateTime;
  date: ADate;
  timezone: Timezone;
  timeEventsInDay: Array<CombinedTimeEventInDayEntry>;
}

function ViewAsCalendarTimeEventInDayColumn(
  props: ViewAsCalendarTimeEventInDayColumnProps
) {
  const theme = useTheme();

  const startOfDay = DateTime.fromISO(`${props.date}T00:00:00`, {
    zone: props.timezone,
  });

  const hours = Array.from({ length: 24 }, (_, i) =>
    startOfDay.plus({ hours: i })
  );

  const timeBlockOffsetsMap = buildTimeBlockOffsetsMap(
    props.timeEventsInDay,
    startOfDay,
    props.timezone
  );

  return (
    <Box
      sx={{
        position: "relative",
        flexGrow: 1,
        height: "96rem",
        minWidth: "7rem",
      }}
    >
      {props.today === props.date && (
        <Box
          sx={{
            position: "absolute",
            top: calendarTimeEventInDayStartMinutesToRems(
              props.rightNow.diff(startOfDay).as("minutes")
            ),
            height: "0.15rem",
            width: "100%",
            backgroundColor: theme.palette.info.dark,
            zIndex: theme.zIndex.appBar,
          }}
        ></Box>
      )}

      {hours.map((hour, idx) => (
        <Box
          key={idx}
          sx={{
            position: "absolute",
            height: "0.05rem",
            left: "-0.05rem", // Offset for gap: 0.1 in container
            backgroundColor: theme.palette.text.disabled,
            top: `${idx * 4}rem`,
            width: "calc(100% + 0.1rem)", // Offset for gap 0.1 in container
          }}
        ></Box>
      ))}

      {props.timeEventsInDay.map((entry, index) => (
        <ViewAsCalendarTimeEventInDayCell
          key={index}
          offset={timeBlockOffsetsMap.get(entry.time_event.ref_id) || 0}
          startOfDay={startOfDay}
          timezone={props.timezone}
          entry={entry}
        />
      ))}
    </Box>
  );
}

interface ViewAsCalendarTimeEventInDayCellProps {
  offset: number;
  startOfDay: DateTime;
  timezone: Timezone;
  entry: CombinedTimeEventInDayEntry;
}

function ViewAsCalendarTimeEventInDayCell(
  props: ViewAsCalendarTimeEventInDayCellProps
) {
  const [query] = useSearchParams();
  const theme = useTheme();
  const containerRef = useRef<HTMLDivElement>(null);

  const [containerWidth, setContainerWidth] = useState(120);
  useEffect(() => {
    setContainerWidth(containerRef.current?.clientWidth || 120);
  }, [containerRef]);

  switch (props.entry.time_event.namespace) {
    case TimeEventNamespace.SCHEDULE_EVENT_IN_DAY:
      const scheduleEntry = props.entry.entry as ScheduleInDayEventEntry;

      const startTime = DateTime.fromISO(
        `${scheduleEntry.time_event.start_date}T${scheduleEntry.time_event.start_time_in_day}`,
        { zone: props.timezone }
      );
      const endTime = startTime.plus({
        minutes: props.entry.time_event.duration_mins,
      });
      const minutesSinceStartOfDay = startTime
        .diff(props.startOfDay)
        .as("minutes");

      const clippedName = clipTimeEventInDayNameToWhatFits(
        startTime,
        endTime,
        scheduleEntry.event.name,
        theme.typography.htmlFontSize,
        containerWidth,
        minutesSinceStartOfDay,
        scheduleEntry.time_event.duration_mins
      );

      return (
        <Box
          ref={containerRef}
          sx={{
            fontSize: "12px",
            position: "absolute",
            top: calendarTimeEventInDayStartMinutesToRems(
              minutesSinceStartOfDay
            ),
            height: calendarTimeEventInDayDurationToRems(
              minutesSinceStartOfDay,
              scheduleEntry.time_event.duration_mins
            ),
            backgroundColor: scheduleStreamColorHex(scheduleEntry.stream.color),
            borderRadius: "0.25rem",
            border: `1px solid ${theme.palette.background.paper}`,
            minWidth: `calc(7rem - ${props.offset * 0.8}rem)`,
            width: `calc(100% - ${props.offset * 0.8}rem)`,
            marginLeft: `${props.offset * 0.8}rem`,
            zIndex: props.offset,
          }}
        >
          <EntityLink
            key={`schedule-event-in-day-${scheduleEntry.event.ref_id}`}
            to={`/workspace/calendar/schedule/event-in-day/${scheduleEntry.event.ref_id}?${query}`}
          >
            <Box
              sx={{
                position: "absolute",
                width: "100%",
                height: "100%",
                top: "0.25rem",
                left: "0.25rem",
                overflow: "hidden",
              }}
            >
              <EntityNameComponent
                name={clippedName}
                color={scheduleStreamColorContrastingHex(
                  scheduleEntry.stream.color
                )}
              />
            </Box>
          </EntityLink>
        </Box>
      );

    case TimeEventNamespace.INBOX_TASK:
      throw new Error("Not implemented");

    default:
      throw new Error("Unexpected namespace");
  }
}

interface ViewAsCalendarMoreButtonProps {
  showAllTimeEventFullDays: boolean;
  setShowAllTimeEventFullDays: React.Dispatch<React.SetStateAction<boolean>>;
}

function ViewAsCalendarMoreButton(props: ViewAsCalendarMoreButtonProps) {
  return (
    <Button
      variant="outlined"
      sx={{
        width: "3.5rem",
        minWidth: "3.5rem",
        height: "3.5rem",
        alignSelf: "end",
      }}
      onClick={() => props.setShowAllTimeEventFullDays((c) => !c)}
    >
      {props.showAllTimeEventFullDays ? "Show Less" : "Show More"}
    </Button>
  );
}

function ViewAsCalendarDaysAndFullDaysContiner(props: PropsWithChildren) {
  const theme = useTheme();
  const isBigScreen = useBigScreen();

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        position: "sticky",
        minWidth: isBigScreen ? undefined : "fit-content",
        top: isBigScreen ? "-0.5rem" : "0px",
        backgroundColor: theme.palette.background.paper,
        zIndex: theme.zIndex.appBar + 200,
        borderBottom: "1px solid darkgray",
      }}
    >
      {props.children}
    </Box>
  );
}

function ViewAsCalendarInDayContainer(props: PropsWithChildren) {
  const isBigScreen = useBigScreen();

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "row",
        gap: "0.1rem",
        position: "relative",
        minWidth: isBigScreen ? undefined : "fit-content",
      }}
    >
      {props.children}
    </Box>
  );
}

interface ViewAsCalendarGoToCellProps {
  label: string;
  period: RecurringTaskPeriod;
  periodStart: string;
  calendarLocation: string;
}

function ViewAsCalendarGoToCell(props: ViewAsCalendarGoToCellProps) {
  return (
    <Box
      sx={{
        minWidth: "3rem",
        height: "100%",
        border: "1px solid darkgray",
        borderRadius: "0.25rem",
        display: "flex",
        justifyContent: "center",
      }}
    >
      <EntityLink
        to={`/workspace/calendar${props.calendarLocation}?today=${props.periodStart}&period=${props.period}&view=calendar`}
      >
        <Typography variant="h6">{props.label}</Typography>
      </EntityLink>
    </Box>
  );
}

interface ViewAsCalendarStatsCellProps {
  label: string;
  forceColumn: boolean;
  showCompact: boolean;
  stats: CalendarEventsStatsPerSubperiod;
  calendarLocation: string;
}

function ViewAsCalendarStatsCell(props: ViewAsCalendarStatsCellProps) {
  return (
    <Box
      sx={{
        border: "1px solid darkgray",
        borderRadius: "0.25rem",
        display: "flex",
        flexDirection: "column",
        gap: "0.25rem",
        padding: "0.25rem",
        justifyContent: "center",
      }}
    >
      <Typography variant="h6">{props.label}</Typography>
      <ViewAsStatsPerSubperiod
        forceColumn={props.forceColumn}
        showCompact={props.showCompact}
        view={View.CALENDAR}
        stats={props.stats}
        calendarLocation={props.calendarLocation}
      />
    </Box>
  );
}

function ViewAsCalendarEmptyCell() {
  return <Box sx={{ minWidth: "3.5rem" }}></Box>;
}

function ViewAsScheduleDailyAndWeekly(props: ViewAsProps) {
  const isBigScreen = useBigScreen();

  if (props.entries === undefined) {
    throw new Error("Entries are required");
  }

  const combinedTimeEventFullDays: Array<CombinedTimeEventFullDaysEntry> = [];
  for (const entry of props.entries.schedule_event_full_days_entries) {
    combinedTimeEventFullDays.push({
      time_event: entry.time_event,
      entry: entry,
    });
  }
  for (const entry of props.entries.person_entries) {
    combinedTimeEventFullDays.push({
      time_event: entry.birthday_time_event,
      entry: entry,
    });
  }

  const combinedTimeEventInDay: Array<CombinedTimeEventInDayEntry> = [];
  for (const entry of props.entries.schedule_event_in_day_entries) {
    combinedTimeEventInDay.push({
      time_event: entry.time_event,
      entry: entry,
    });
  }
  for (const entry of props.entries.inbox_task_entries) {
    for (const timeEvent of entry.time_events) {
      combinedTimeEventInDay.push({
        time_event: timeEvent,
        entry: entry,
      });
    }
  }

  const daysToProcess = allDaysBetween(
    props.periodStartDate,
    props.periodEndDate
  );
  const partitionedCombinedTimeEventFullDays =
    combinedTimeEventFullDayEntryPartionByDay(combinedTimeEventFullDays);
  const partitionedCombinedTimeEventInDay =
    combinedTimeEventInDayEntryPartionByDay(
      combinedTimeEventInDay,
      props.timezone
    );

  return (
    <TableContainer component={Paper}>
      <Table sx={{ borderCollapse: "separate", borderSpacing: "0.2rem" }}>
        <TableBody>
          {daysToProcess.map((date) => {
            const partitionFullDays =
              partitionedCombinedTimeEventFullDays[date] || [];
            const partitionInDay =
              partitionedCombinedTimeEventInDay[date] || [];

            if (partitionFullDays.length === 0 && partitionInDay.length === 0) {
              return <React.Fragment key={date}></React.Fragment>;
            }

            const firstRowFullDays = partitionFullDays[0];
            const otherRowsFullDays = partitionFullDays.slice(1);
            const firstRowInDay = partitionInDay[0];
            const otherRowsInDay = partitionInDay.slice(1);

            return (
              <React.Fragment key={date}>
                {firstRowFullDays && (
                  <>
                    <TableRow>
                      <ViewAsScheduleDateCell
                        rowSpan={
                          partitionFullDays.length + partitionInDay.length
                        }
                        isbigscreen={isBigScreen.toString()}
                      >
                        {date}
                      </ViewAsScheduleDateCell>

                      <ViewAsScheduleTimeEventFullDaysRows
                        entry={firstRowFullDays}
                      />
                    </TableRow>

                    {otherRowsFullDays.map((entry, index) => (
                      <TableRow key={index}>
                        <ViewAsScheduleTimeEventFullDaysRows entry={entry} />
                      </TableRow>
                    ))}

                    {firstRowInDay && (
                      <TableRow>
                        <ViewAsScheduleTimeEventInDaysRows
                          entry={firstRowInDay}
                          timezone={props.timezone}
                        />
                      </TableRow>
                    )}

                    {otherRowsInDay.map((entry, index) => (
                      <TableRow key={index}>
                        <ViewAsScheduleTimeEventInDaysRows
                          entry={entry}
                          timezone={props.timezone}
                        />
                      </TableRow>
                    ))}
                  </>
                )}

                {firstRowFullDays === undefined && firstRowInDay && (
                  <>
                    <TableRow>
                      <TableCell
                        rowSpan={partitionInDay.length}
                        sx={{ verticalAlign: "top" }}
                      >
                        {date}
                      </TableCell>

                      <ViewAsScheduleTimeEventInDaysRows
                        entry={firstRowInDay}
                        timezone={props.timezone}
                      />
                    </TableRow>

                    {otherRowsInDay.map((entry, index) => (
                      <TableRow key={index}>
                        <ViewAsScheduleTimeEventInDaysRows
                          entry={entry}
                          timezone={props.timezone}
                        />
                      </TableRow>
                    ))}
                  </>
                )}
              </React.Fragment>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

function ViewAsScheduleMonthlyQuarterlyAndYearly(props: ViewAsProps) {
  const isBigScreen = useBigScreen();

  if (props.stats === undefined) {
    throw new Error("Stats are required");
  }

  return (
    <TableContainer component={Paper}>
      <Table sx={{ borderCollapse: "separate", borderSpacing: "0.2rem" }}>
        <TableBody>
          {props.stats.per_subperiod.map((stats, index) => {
            return (
              <TableRow key={index}>
                <ViewAsScheduleDateCell isbigscreen={isBigScreen.toString()}>
                  {stats.period_start_date}
                </ViewAsScheduleDateCell>

                <ViewAsScheduleContentCell>
                  <ViewAsStatsPerSubperiod
                    forceColumn={false}
                    showCompact={!isBigScreen}
                    view={View.SCHEDULE}
                    stats={stats}
                    calendarLocation={props.calendarLocation}
                  />
                </ViewAsScheduleContentCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

interface ViewAsScheduleTimeEventFullDaysRowsProps {
  entry: CombinedTimeEventFullDaysEntry;
}

function ViewAsScheduleTimeEventFullDaysRows(
  props: ViewAsScheduleTimeEventFullDaysRowsProps
) {
  const [query] = useSearchParams();
  const isBigScreen = useBigScreen();

  switch (props.entry.time_event.namespace) {
    case TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK:
      const fullDaysEntry = props.entry.entry as ScheduleFullDaysEventEntry;
      return (
        <React.Fragment>
          <ViewAsScheduleTimeCell isbigscreen={isBigScreen.toString()}>
            [All Day]
          </ViewAsScheduleTimeCell>

          <ViewAsScheduleEventCell
            color={scheduleStreamColorHex(fullDaysEntry.stream.color)}
            isbigscreen={isBigScreen.toString()}
            height="0.25rem"
          >
            <EntityLink
              light
              key={`schedule-event-full-days-${fullDaysEntry.event.ref_id}`}
              to={`/workspace/calendar/schedule/event-full-days/${fullDaysEntry.event.ref_id}?${query}`}
            >
              <EntityNameComponent
                name={fullDaysEntry.event.name}
                color={scheduleStreamColorContrastingHex(
                  fullDaysEntry.stream.color
                )}
              />
            </EntityLink>
          </ViewAsScheduleEventCell>
        </React.Fragment>
      );

    case TimeEventNamespace.PERSON_BIRTHDAY:
      throw new Error("Not implemented");

    default:
      throw new Error("Unexpected namespace");
  }
}

interface ViewAsScheduleTimeEventInDaysRowsProps {
  entry: CombinedTimeEventInDayEntry;
  timezone: Timezone;
}

function ViewAsScheduleTimeEventInDaysRows(
  props: ViewAsScheduleTimeEventInDaysRowsProps
) {
  const [query] = useSearchParams();
  const isBigScreen = useBigScreen();

  const startTime = DateTime.fromISO(
    `${props.entry.time_event.start_date}T${props.entry.time_event.start_time_in_day}`,
    { zone: props.timezone }
  );
  const endTime = startTime.plus({
    minutes: props.entry.time_event.duration_mins,
  });

  switch (props.entry.time_event.namespace) {
    case TimeEventNamespace.SCHEDULE_EVENT_IN_DAY:
      const scheduleEntry = props.entry.entry as ScheduleInDayEventEntry;
      return (
        <React.Fragment>
          <ViewAsScheduleTimeCell isbigscreen={isBigScreen.toString()}>
            [{startTime.toFormat("HH:mm")} - {endTime.toFormat("HH:mm")}]
          </ViewAsScheduleTimeCell>

          <ViewAsScheduleEventCell
            color={scheduleStreamColorHex(scheduleEntry.stream.color)}
            isbigscreen={isBigScreen.toString()}
            height={scheduleTimeEventInDayDurationToRems(
              scheduleEntry.time_event.duration_mins
            )}
          >
            <EntityLink
              light
              key={`schedule-event-in-day-${scheduleEntry.event.ref_id}`}
              to={`/workspace/calendar/schedule/event-in-day/${scheduleEntry.event.ref_id}?${query}`}
            >
              <EntityNameComponent
                name={scheduleEntry.event.name}
                color={scheduleStreamColorContrastingHex(
                  scheduleEntry.stream.color
                )}
              />
            </EntityLink>
          </ViewAsScheduleEventCell>
        </React.Fragment>
      );

    case TimeEventNamespace.INBOX_TASK:
      throw new Error("Not implemented");

    default:
      throw new Error("Unexpected namespace");
  }
}

interface ViewAsScheduleDateCellProps {
  isbigscreen: string;
}

const ViewAsScheduleDateCell = styled(TableCell)<ViewAsScheduleDateCellProps>(
  ({ isbigscreen }) => ({
    verticalAlign: "top",
    padding: "0.25rem",
    width: isbigscreen === "true" ? "15%" : "25%",
  })
);

const ViewAsScheduleContentCell = styled(TableCell)({
  padding: "0.25rem",
});

interface ViewAsScheduleTimeCellProps {
  isbigscreen: string;
}

const ViewAsScheduleTimeCell = styled(TableCell)<ViewAsScheduleTimeCellProps>(
  ({ isbigscreen }) => ({
    verticalAlign: "top",
    padding: "0.25rem",
    width: isbigscreen === "true" ? "15%" : "30%",
  })
);

interface ViewAsScheduleEventCellProps {
  isbigscreen: string;
  color: string;
  height: string;
}

const ViewAsScheduleEventCell = styled(TableCell)<ViewAsScheduleEventCellProps>(
  ({ isbigscreen, color, height }) => ({
    verticalAlign: "top",
    backgroundColor: color,
    padding: "0.25rem",
    paddingLeft: "0.5rem",
    paddingBottom: height,
    borderRadius: "0.25rem",
  })
);

interface ViewAsStatsPerSubperiodProps {
  forceColumn: boolean;
  showCompact: boolean;
  view: View;
  stats: CalendarEventsStatsPerSubperiod;
  calendarLocation: string;
}

function ViewAsStatsPerSubperiod(props: ViewAsStatsPerSubperiodProps) {
  return (
    <EntityLink
      to={`/workspace/calendar${props.calendarLocation}?today=${props.stats.period_start_date}&period=${props.stats.period}&view=${props.view}`}
    >
      <Box
        sx={{
          display: "flex",
          flexDirection: props.forceColumn ? "column" : "row",
          gap: "0.25rem",
          flexWrap: "wrap",
        }}
      >
        <span>
          📅 {props.stats.schedule_event_full_days_cnt}{" "}
          {!props.showCompact ? "from scheduled full day events" : ""}
        </span>
        <span>
          ⌚ {props.stats.schedule_event_in_day_cnt}{" "}
          {!props.showCompact ? "from scheduled in day events" : ""}
        </span>
        <span>
          📥 {props.stats.inbox_task_cnt}{" "}
          {!props.showCompact ? "from inbox task" : ""}
        </span>
        <span>
          👨 {props.stats.person_birthday_cnt}{" "}
          {!props.showCompact ? "from birthdays" : ""}
        </span>
      </Box>
    </EntityLink>
  );
}

function calculateStartTimeInTimezone(
  timeEvent: TimeEventInDayBlock,
  timezone: Timezone
): DateTime {
  return DateTime.fromISO(
    `${timeEvent.start_date}T${timeEvent.start_time_in_day}`,
    { zone: timezone }
  );
}

function calculateEndTimeInTimezone(
  timeEvent: TimeEventInDayBlock,
  timezone: Timezone
): DateTime {
  const startTime = DateTime.fromISO(
    `${timeEvent.start_date}T${timeEvent.start_time_in_day}`,
    { zone: timezone }
  );

  const endTime = startTime.plus({ minutes: timeEvent.duration_mins });

  return endTime;
}

function computeTimeEventInDayDurationInQuarters(
  minutesSinceStartOfDay: number,
  durationMins: number
): number {
  // Each 15 minutes is 1 rem. Display has 96=4*24 rem height.
  // If the event goes beyond the day, we cap it at 24 hours.
  const finalOffsetInMinutes = minutesSinceStartOfDay + durationMins;
  let finalDurationInMins = durationMins;
  if (finalOffsetInMinutes > 24 * 60) {
    finalDurationInMins = Math.max(15, 24 * 60 - minutesSinceStartOfDay);
  }
  return Math.max(2, finalDurationInMins / 15);
}

function clipTimeEventFullDaysNameToWhatFits(
  name: string,
  fontSize: number,
  containerWidth: number
): string {
  const textWidthInPx = measureText(name, fontSize);

  if (textWidthInPx <= containerWidth) {
    return name;
  } else {
    // Do some rough approximation here.
    const maxChars = Math.floor((name.length * containerWidth) / textWidthInPx);
    return `${name.substring(0, maxChars)} ...`;
  }
}

function clipTimeEventInDayNameToWhatFits(
  startTime: DateTime,
  endTime: DateTime,
  name: string,
  fontSize: number,
  containerWidth: number,
  minutesSinceStartOfDay: number,
  durationInMins: number
): string {
  const durationInQuarters = computeTimeEventInDayDurationInQuarters(
    0,
    durationInMins
  );
  const durationInHalfs = Math.max(1, Math.floor(durationInQuarters / 2));

  const bigName = `[${startTime.toFormat("HH:mm")} - ${endTime.toFormat(
    "HH:mm"
  )}] ${name}`;
  const textWidthInPx = measureText(bigName, fontSize);
  const totalWidthInPx = containerWidth * durationInHalfs;

  if (textWidthInPx <= totalWidthInPx) {
    return bigName;
  } else {
    // Do some rough approximation here.
    const maxChars = Math.max(
      3,
      Math.floor((name.length * totalWidthInPx) / textWidthInPx)
    );
    return `[${startTime.toFormat("HH:mm")}] ${name.substring(
      0,
      maxChars
    )} ...`;
  }
}

function calendarTimeEventInDayStartMinutesToRems(startMins: number): string {
  // Each 15 minutes is 1 rem. Display has 96=4*24 rem height.
  const startHours = Math.max(0, startMins / 15);
  return `${startHours}rem`;
}

function calendarTimeEventInDayDurationToRems(
  minutesSinceStartOfDay: number,
  durationMins: number
): string {
  const durationInQuarters = computeTimeEventInDayDurationInQuarters(
    minutesSinceStartOfDay,
    durationMins
  );
  return `${durationInQuarters}rem`;
}

function scheduleTimeEventInDayDurationToRems(durationMins: number): string {
  const durationInHalfs = 0.5 + Math.floor(durationMins / 30);
  return `${durationInHalfs}rem`;
}

interface CombinedTimeEventFullDaysEntry {
  time_event: TimeEventFullDaysBlock;
  entry: ScheduleFullDaysEventEntry | PersonEntry;
}

interface CombinedTimeEventInDayEntry {
  time_event: TimeEventInDayBlock;
  entry: ScheduleInDayEventEntry | InboxTaskEntry;
}

function combinedTimeEventFullDayEntryPartionByDay(
  entries: Array<CombinedTimeEventFullDaysEntry>
): Record<string, Array<CombinedTimeEventFullDaysEntry>> {
  const partition: Record<string, Array<CombinedTimeEventFullDaysEntry>> = {};

  for (const entry of entries) {
    const firstDate = aDateToDate(entry.time_event.start_date);
    for (let idx = 0; idx < entry.time_event.duration_days; idx++) {
      const date = firstDate.plus({ days: idx });

      const dateStr = date.toISODate();
      if (partition[dateStr] === undefined) {
        partition[dateStr] = [];
      }
      partition[dateStr].push(entry);
    }
  }

  return partition;
}

function splitTimeEventInDayEntryIntoPerDayEntries(
  entry: CombinedTimeEventInDayEntry,
  timezone: Timezone
): {
  day1: CombinedTimeEventInDayEntry;
  day2?: CombinedTimeEventInDayEntry;
  day3?: CombinedTimeEventInDayEntry;
} {
  const startTime = calculateStartTimeInTimezone(entry.time_event, timezone);
  const endTime = calculateEndTimeInTimezone(entry.time_event, timezone);

  if (startTime.day === endTime.day) {
    // Here we have only one day.
    return {
      day1: entry,
    };
  } else if (startTime.day + 1 === endTime.day) {
    // Here we have two days.
    const day1TimeEvent = {
      ...entry.time_event,
      duration_mins:
        -1 *
        startTime.diff(startTime.set({ hour: 23, minute: 59 })).as("minutes"),
    };
    const day2TimeEvent = {
      ...entry.time_event,
      start_date: endTime.toISODate(),
      start_time_in_day: "00:00",
      duration_mins: endTime
        .diff(endTime.set({ hour: 0, minute: 0 }))
        .as("minutes"),
    };

    return {
      day1: {
        time_event: day1TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day1TimeEvent,
        },
      },
      day2: {
        time_event: day2TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day2TimeEvent,
        },
      },
    };
  } else if (startTime.day + 2 === endTime.day) {
    // Here we have three days.
    const day1TimeEvent = {
      ...entry.time_event,
      duration_mins:
        -1 *
        startTime.diff(startTime.set({ hour: 23, minute: 59 })).as("minutes"),
    };
    const day2TimeEvent = {
      ...entry.time_event,
      start_date: startTime.plus({ days: 1 }).toISODate(),
      start_time_in_day: "00:00",
      duration_mins: 24 * 60,
    };
    const day3TimeEvent = {
      ...entry.time_event,
      start_date: endTime.toISODate(),
      start_time_in_day: "00:00",
      duration_mins: endTime
        .diff(endTime.set({ hour: 0, minute: 0 }))
        .as("minutes"),
    };

    return {
      day1: {
        time_event: day1TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day1TimeEvent,
        },
      },
      day2: {
        time_event: day2TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day2TimeEvent,
        },
      },
      day3: {
        time_event: day3TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day3TimeEvent,
        },
      },
    };
  } else {
    throw new Error("Unexpected time event duration");
  }
}

function combinedTimeEventInDayEntryPartionByDay(
  entries: Array<CombinedTimeEventInDayEntry>,
  timezone: Timezone
): Record<string, Array<CombinedTimeEventInDayEntry>> {
  const partition: Record<string, Array<CombinedTimeEventInDayEntry>> = {};

  for (const entry of entries) {
    const splitEntries = splitTimeEventInDayEntryIntoPerDayEntries(
      entry,
      timezone
    );

    const dateStr = splitEntries.day1.time_event.start_date;
    if (partition[dateStr] === undefined) {
      partition[dateStr] = [];
    }
    partition[dateStr].push(splitEntries.day1);

    if (splitEntries.day2) {
      const dateStr = splitEntries.day2.time_event.start_date;
      if (partition[dateStr] === undefined) {
        partition[dateStr] = [];
      }
      partition[dateStr].push(splitEntries.day2);
    }

    if (splitEntries.day3) {
      const dateStr = splitEntries.day3.time_event.start_date;
      if (partition[dateStr] === undefined) {
        partition[dateStr] = [];
      }
      partition[dateStr].push(splitEntries.day3);
    }
  }

  // Now sort all partitions.
  for (const dateStr in partition) {
    partition[dateStr] = sortTimeEventInDayByStartTimeAndEndTime(
      partition[dateStr]
    );
  }

  return partition;
}

function sortTimeEventInDayByStartTimeAndEndTime(
  entries: Array<CombinedTimeEventInDayEntry>
) {
  return entries.sort((a, b) => {
    const aStartTime = DateTime.fromISO(
      `${a.time_event.start_date}T${a.time_event.start_time_in_day}`,
      { zone: "UTC" }
    );
    const bStartTime = DateTime.fromISO(
      `${b.time_event.start_date}T${b.time_event.start_time_in_day}`,
      { zone: "UTC" }
    );

    if (aStartTime === bStartTime) {
      const aEndTime = aStartTime.plus({
        minutes: a.time_event.duration_mins,
      });
      const bEndTime = bStartTime.plus({
        minutes: b.time_event.duration_mins,
      });
      return aEndTime < bEndTime ? -1 : 1;
    }
    return aStartTime < bStartTime ? -1 : 1;
  });
}

function buildTimeBlockOffsetsMap(
  entries: Array<CombinedTimeEventInDayEntry>,
  startOfDay: DateTime,
  timezone: Timezone
): Map<EntityId, number> {
  const offsets = new Map<EntityId, number>();

  const freeOffsetsMap = [];
  for (let idx = 0; idx < 24 * 4; idx++) {
    freeOffsetsMap.push({
      time: startOfDay.plus({ minutes: idx * 15 }),
      offset0: false,
      offset1: false,
      offset2: false,
      offset3: false,
      offset4: false,
    });
  }

  for (const entry of entries) {
    const startTime = calculateStartTimeInTimezone(entry.time_event, timezone);
    const minutesSinceStartOfDay = startTime.diff(startOfDay).as("minutes");

    const firstCellIdx = Math.floor(minutesSinceStartOfDay / 15);
    const offsetCell = freeOffsetsMap[firstCellIdx];

    if (offsetCell.offset0 === false) {
      offsets.set(entry.time_event.ref_id, 0);
      offsetCell.offset0 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset0 = true;
      }
      continue;
    } else if (offsetCell.offset1 === false) {
      offsets.set(entry.time_event.ref_id, 1);
      offsetCell.offset1 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset1 = true;
      }
      continue;
    } else if (offsetCell.offset2 === false) {
      offsets.set(entry.time_event.ref_id, 2);
      offsetCell.offset2 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset2 = true;
      }
      continue;
    } else if (offsetCell.offset3 === false) {
      offsets.set(entry.time_event.ref_id, 3);
      offsetCell.offset3 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset3 = true;
      }
      continue;
    } else {
      offsets.set(entry.time_event.ref_id, 4);
      offsetCell.offset4 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset4 = true;
      }
      continue;
    }
  }

  return offsets;
}

function statsSubperiodForPeriod(
  period: RecurringTaskPeriod
): RecurringTaskPeriod | null {
  switch (period) {
    case RecurringTaskPeriod.DAILY:
      return null;
    case RecurringTaskPeriod.WEEKLY:
      return RecurringTaskPeriod.DAILY;
    case RecurringTaskPeriod.MONTHLY:
      return RecurringTaskPeriod.DAILY;
    case RecurringTaskPeriod.QUARTERLY:
      return RecurringTaskPeriod.WEEKLY;
    case RecurringTaskPeriod.YEARLY:
      return RecurringTaskPeriod.MONTHLY;
  }
}

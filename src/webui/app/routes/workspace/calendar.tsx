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
  Timezone,
  VacationEntry,
} from "@jupiter/webapi-client";
import {
  AppPlatform,
  RecurringTaskPeriod,
  TimeEventNamespace,
} from "@jupiter/webapi-client";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import TuneIcon from "@mui/icons-material/Tune";
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
  useNavigate,
  useSearchParams,
  useTransition,
} from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { DateTime } from "luxon";
import type { PropsWithChildren } from "react";
import React, { useContext, useEffect, useRef, useState } from "react";
import { z } from "zod";
import { parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
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
import { TimeEventParamsNewPlaceholder } from "~/components/time-event-params-new-placeholder";
import {
  aDateToDate,
  allDaysBetween,
  compareADate,
} from "~/logic/domain/adate";
import { newURLParams } from "~/logic/domain/navigation";
import { periodName } from "~/logic/domain/period";
import {
  scheduleStreamColorContrastingHex,
  scheduleStreamColorHex,
} from "~/logic/domain/schedule-stream-color";
import type {
  CombinedTimeEventFullDaysEntry,
  CombinedTimeEventInDayEntry,
} from "~/logic/domain/time-event";
import {
  birthdayTimeEventName,
  BIRTHDAY_TIME_EVENT_COLOR,
  calculateEndTimeForTimeEvent,
  calculateStartTimeForTimeEvent,
  calendarPxHeightToMinutes,
  calendarTimeEventInDayDurationToRems,
  calendarTimeEventInDayStartMinutesToRems,
  compareNamespaceForSortingFullDaysTimeEvents,
  INBOX_TASK_TIME_EVENT_COLOR,
  scheduleTimeEventInDayDurationToRems,
  timeEventInDayBlockToTimezone,
  VACATION_TIME_EVENT_COLOR,
} from "~/logic/domain/time-event";
import { inferPlatform } from "~/logic/frontdoor.server";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowBranch,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
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
  date: z
    .string()
    .regex(/[0-9][0-9][0-9][0-9][-][0-9][0-9][-][0-9][0-9]/)
    .optional(),
  period: z.nativeEnum(RecurringTaskPeriod).optional(),
  view: z.nativeEnum(View).optional(),
};

export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const query = parseQuery(request, QuerySchema);
  const url = new URL(request.url);

  const platform = inferPlatform(request.headers.get("User-Agent"));

  if (
    query.date === undefined ||
    query.period === undefined ||
    query.view === undefined
  ) {
    // We do it like this so we keep the query params that are already there.
    url.searchParams.set("date", query.date || DateTime.now().toISODate());
    url.searchParams.set(
      "period",
      query.period ||
        (platform === AppPlatform.MOBILE_IOS ||
        platform === AppPlatform.MOBILE_ANDROID
          ? RecurringTaskPeriod.DAILY
          : RecurringTaskPeriod.WEEKLY)
    );
    url.searchParams.set("view", query.view || View.CALENDAR);

    return redirect(url.pathname + url.search);
  }

  const response = await apiClient.calendar.calendarLoadForDateAndPeriod({
    right_now: query.date,
    period: query.period,
    stats_subperiod: statsSubperiodForPeriod(query.period),
  });

  return json({
    date: query.date as string,
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

  const rightNow = DateTime.local({ zone: topLevelInfo.user.timezone });
  const theRealToday = rightNow.toISODate() as ADate;

  return (
    <TrunkPanel
      key="calendar"
      createLocation={`/workspace/calendar/schedule/event-in-day/new?${query}`}
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
                  text: "New External Calendar Stream",
                  link: `/workspace/calendar/schedule/stream/new-external?${query}`,
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
                  link: `/workspace/calendar${calendarLocation}?${newURLParams(
                    query,
                    "date",
                    theRealToday
                  )}`,
                }),
                NavSingle({
                  text: "Prev",
                  icon: <ArrowBackIcon />,
                  link: `/workspace/calendar${calendarLocation}?${newURLParams(
                    query,
                    "date",
                    loaderData.prevPeriodStartDate
                  )}`,
                }),
                NavSingle({
                  text: "Next",
                  icon: <ArrowForwardIcon />,
                  link: `/workspace/calendar${calendarLocation}?${newURLParams(
                    query,
                    "date",
                    loaderData.nextPeriodStartDate
                  )}`,
                }),
              ],
            }),
            NavMultipleCompact({
              navs: [
                NavSingle({
                  text: periodName(RecurringTaskPeriod.DAILY),
                  highlight: loaderData.period === RecurringTaskPeriod.DAILY,
                  link: `/workspace/calendar${calendarLocation}?${newURLParams(
                    query,
                    "period",
                    RecurringTaskPeriod.DAILY
                  )}`,
                }),
                NavSingle({
                  text: periodName(RecurringTaskPeriod.WEEKLY),
                  highlight: loaderData.period === RecurringTaskPeriod.WEEKLY,
                  link: `/workspace/calendar${calendarLocation}?${newURLParams(
                    query,
                    "period",
                    RecurringTaskPeriod.WEEKLY
                  )}`,
                }),
                NavSingle({
                  text: periodName(RecurringTaskPeriod.MONTHLY),
                  highlight: loaderData.period === RecurringTaskPeriod.MONTHLY,
                  link: `/workspace/calendar${calendarLocation}?${newURLParams(
                    query,
                    "period",
                    RecurringTaskPeriod.MONTHLY
                  )}`,
                }),
                NavSingle({
                  text: periodName(RecurringTaskPeriod.QUARTERLY),
                  highlight:
                    loaderData.period === RecurringTaskPeriod.QUARTERLY,
                  link: `/workspace/calendar${calendarLocation}?${newURLParams(
                    query,
                    "period",
                    RecurringTaskPeriod.QUARTERLY
                  )}`,
                }),
                NavSingle({
                  text: periodName(RecurringTaskPeriod.YEARLY),
                  highlight: loaderData.period === RecurringTaskPeriod.YEARLY,
                  link: `/workspace/calendar${calendarLocation}?${newURLParams(
                    query,
                    "period",
                    RecurringTaskPeriod.YEARLY
                  )}`,
                }),
              ],
            }),
            NavMultipleCompact({
              navs: [
                NavSingle({
                  text: "Calendar",
                  link: `/workspace/calendar${calendarLocation}?${newURLParams(
                    query,
                    "view",
                    View.CALENDAR
                  )}`,
                  highlight: loaderData.view === View.CALENDAR,
                }),
                NavSingle({
                  text: "Schedule",
                  link: `/workspace/calendar${calendarLocation}?${newURLParams(
                    query,
                    "view",
                    View.SCHEDULE
                  )}`,
                  highlight: loaderData.view === View.SCHEDULE,
                }),
              ],
            }),
            NavSingle({
              text: "Settings",
              link: `/workspace/calendar/settings`,
              icon: <TuneIcon />,
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
              rightNow={rightNow}
              timezone={topLevelInfo.user.timezone}
              today={theRealToday}
              period={loaderData.period}
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
              rightNow={rightNow}
              today={theRealToday}
              period={loaderData.period}
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
              rightNow={rightNow}
              today={theRealToday}
              period={loaderData.period}
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
              rightNow={rightNow}
              today={theRealToday}
              period={loaderData.period}
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
              rightNow={rightNow}
              today={theRealToday}
              period={loaderData.period}
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
              rightNow={rightNow}
              today={theRealToday}
              period={loaderData.period}
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
              rightNow={rightNow}
              today={theRealToday}
              period={loaderData.period}
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
  rightNow: DateTime;
  today: ADate;
  timezone: Timezone;
  period: RecurringTaskPeriod;
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

  const periodStartDate = DateTime.fromISO(props.periodStartDate);

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
  for (const entry of props.entries.vacation_entries) {
    combinedTimeEventFullDays.push({
      time_event: entry.time_event,
      entry: entry,
    });
  }

  const combinedTimeEventInDay: Array<CombinedTimeEventInDayEntry> = [];
  for (const entry of props.entries.schedule_event_in_day_entries) {
    combinedTimeEventInDay.push({
      time_event_in_tz: timeEventInDayBlockToTimezone(
        entry.time_event,
        props.timezone
      ),
      entry: entry,
    });
  }
  for (const entry of props.entries.inbox_task_entries) {
    for (const timeEvent of entry.time_events) {
      combinedTimeEventInDay.push({
        time_event_in_tz: timeEventInDayBlockToTimezone(
          timeEvent,
          props.timezone
        ),
        entry: entry,
      });
    }
  }

  const partitionedCombinedTimeEventFullDays =
    combinedTimeEventFullDayEntryPartionByDay(combinedTimeEventFullDays);
  const thePartititionFullDays =
    partitionedCombinedTimeEventFullDays[props.periodStartDate] || [];
  const partitionedCombinedTimeEventInDay =
    combinedTimeEventInDayEntryPartionByDay(combinedTimeEventInDay);
  const thePartitionInDay =
    partitionedCombinedTimeEventInDay[props.periodStartDate] || [];

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
          <ViewAsCalendarEmptyCell>
            <Typography variant="h6">
              {periodStartDate.toFormat("MMM")}
            </Typography>
            <Typography variant="h6">
              {periodStartDate.toFormat("yyyy")}
            </Typography>
          </ViewAsCalendarEmptyCell>
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
            showAll={showAllTimeEventFullDays}
            maxFullDaysEntriesCnt={thePartititionFullDays.length}
            timeEventFullDays={thePartititionFullDays}
          />

          <ViewAsCalendarEmptyCell />
        </Box>
      </ViewAsCalendarDaysAndFullDaysContiner>

      <ViewAsCalendarInDayContainer>
        <ViewAsCalendarLeftColumn />
        <ViewAsCalendarTimeEventInDayColumn
          rightNow={props.rightNow}
          today={props.today}
          timezone={props.timezone}
          date={props.periodStartDate}
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

  const periodStartDate = DateTime.fromISO(props.periodStartDate);
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
  for (const entry of props.entries.vacation_entries) {
    combinedTimeEventFullDays.push({
      time_event: entry.time_event,
      entry: entry,
    });
  }

  const combinedTimeEventInDay: Array<CombinedTimeEventInDayEntry> = [];
  for (const entry of props.entries.schedule_event_in_day_entries) {
    combinedTimeEventInDay.push({
      time_event_in_tz: timeEventInDayBlockToTimezone(
        entry.time_event,
        props.timezone
      ),
      entry: entry,
    });
  }
  for (const entry of props.entries.inbox_task_entries) {
    for (const timeEvent of entry.time_events) {
      combinedTimeEventInDay.push({
        time_event_in_tz: timeEventInDayBlockToTimezone(
          timeEvent,
          props.timezone
        ),
        entry: entry,
      });
    }
  }

  const partitionedCombinedTimeEventFullDays =
    combinedTimeEventFullDayEntryPartionByDay(combinedTimeEventFullDays);
  const partitionedCombinedTimeEventInDay =
    combinedTimeEventInDayEntryPartionByDay(combinedTimeEventInDay);

  const maxFullDaysEntriesCnt = Math.max(
    ...Object.values(partitionedCombinedTimeEventFullDays).map(
      (entries) => entries.length
    )
  );

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
          <ViewAsCalendarEmptyCell>
            <Typography variant="h6">
              {periodStartDate.toFormat("MMM")}
            </Typography>
            <Typography variant="h6">
              {periodStartDate.toFormat("yyyy")}
            </Typography>
          </ViewAsCalendarEmptyCell>
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
        <ViewAsCalendarLeftColumn />

        {allDays.map((date, idx) => (
          <ViewAsCalendarTimeEventInDayColumn
            key={idx}
            rightNow={props.rightNow}
            today={props.today}
            timezone={props.timezone}
            date={date}
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
    <>
      <Typography variant="h5">
        Viewing {periodStartDate.monthLong} {periodStartDate.year}
      </Typography>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns:
            "3rem [mon] 1fr [tue] 1fr [wed] 1fr [thu] 1fr [fri] 1fr [sat] 1fr [sun] 1fr",
          gridTemplateRows: "auto",
          gridGap: "0.25rem",
        }}
      >
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
            let lastDay = startDate.endOf("week").day as number;
            if (lastDay < startDate.day) {
              lastDay = (startDate.daysInMonth as number) + lastDay;
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
    </>
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
    <>
      <Typography variant="h5">
        Viewing {monthToQuarter(periodStartDate.month)} {periodStartDate.year}
      </Typography>
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
    </>
  );
}

function ViewAsCalendarYearly(props: ViewAsProps) {
  const isBigScreen = useBigScreen();

  if (props.stats === undefined) {
    throw new Error("Stats are required");
  }

  const periodStartDate = DateTime.fromISO(props.periodStartDate);

  return (
    <>
      <Typography variant="h5">Viewing {periodStartDate.year}</Typography>
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
    </>
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

interface ViewAsCalendarLeftColumnProps {}

function ViewAsCalendarLeftColumn(props: ViewAsCalendarLeftColumnProps) {
  const theme = useTheme();
  const hours = Array.from({ length: 24 }, (_, i) =>
    DateTime.utc(1987, 9, 18, i, 0, 0)
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
        zIndex: theme.zIndex.appBar + 10,
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
          <ViewAsCalendarTimeEventFullDaysCell key={index} entry={entry} />
        );
      })}
    </Box>
  );
}

interface ViewAsCalendarTimeEventFullDaysCellProps {
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
    case TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK: {
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
            fontSize: "10px",
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
    }

    case TimeEventNamespace.PERSON_BIRTHDAY: {
      const fullDaysEntry = props.entry.entry as PersonEntry;

      const clippedName = clipTimeEventFullDaysNameToWhatFits(
        `👨 ${birthdayTimeEventName(
          props.entry.time_event,
          fullDaysEntry.person
        )}`,
        12,
        containerWidth - 32 // A hack of sorts
      );

      return (
        <Box
          ref={containerRef}
          sx={{
            minWidth: "7rem",
            fontSize: "10px",
            backgroundColor: scheduleStreamColorHex(BIRTHDAY_TIME_EVENT_COLOR),
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
            key={`person-birthday-event-${fullDaysEntry.person.ref_id}`}
            to={`/workspace/calendar/time-event/full-days-block/${fullDaysEntry.birthday_time_event.ref_id}?${query}`}
          >
            <EntityNameComponent
              name={clippedName}
              color={scheduleStreamColorContrastingHex(
                BIRTHDAY_TIME_EVENT_COLOR
              )}
            />
          </EntityLink>
        </Box>
      );
    }

    case TimeEventNamespace.VACATION: {
      const fullDaysEntry = props.entry.entry as VacationEntry;

      const clippedName = clipTimeEventFullDaysNameToWhatFits(
        `🌴 ${fullDaysEntry.vacation.name}`,
        12,
        containerWidth - 32 // A hack of sorts
      );

      return (
        <Box
          ref={containerRef}
          sx={{
            minWidth: "7rem",
            fontSize: "10px",
            backgroundColor: scheduleStreamColorHex(VACATION_TIME_EVENT_COLOR),
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
            key={`vacation-event-${fullDaysEntry.time_event.ref_id}`}
            to={`/workspace/calendar/time-event/full-days-block/${fullDaysEntry.time_event.ref_id}?${query}`}
          >
            <EntityNameComponent
              name={clippedName}
              color={scheduleStreamColorContrastingHex(
                VACATION_TIME_EVENT_COLOR
              )}
            />
          </EntityLink>
        </Box>
      );
    }

    default:
      throw new Error("Unknown namespace");
  }
}

interface ViewAsCalendarTimeEventInDayColumnProps {
  rightNow: DateTime;
  today: ADate;
  timezone: Timezone;
  date: ADate;
  timeEventsInDay: Array<CombinedTimeEventInDayEntry>;
}

function ViewAsCalendarTimeEventInDayColumn(
  props: ViewAsCalendarTimeEventInDayColumnProps
) {
  const theme = useTheme();
  const location = useLocation();
  const [query] = useSearchParams();
  const navigate = useNavigate();
  const wholeColumnRef = useRef<HTMLDivElement>(null);

  const startOfDay = DateTime.fromISO(`${props.date}T00:00:00`, {
    zone: "UTC",
  });

  const hours = Array.from({ length: 24 }, (_, i) =>
    startOfDay.plus({ hours: i })
  );

  const timeBlockOffsetsMap = buildTimeBlockOffsetsMap(
    props.timeEventsInDay,
    startOfDay
  );

  const theMinutes = props.rightNow
    .diff(DateTime.fromISO(`${props.today}T00:00`, { zone: props.timezone }))
    .as("minutes");

  function createNewFromDoubleClick(event: React.MouseEvent) {
    if (wholeColumnRef.current === null) {
      return;
    }
    if (wholeColumnRef.current !== event.target) {
      return;
    }

    const minutes = calendarPxHeightToMinutes(
      event.nativeEvent.offsetY,
      theme.typography.htmlFontSize
    );
    const time = startOfDay.plus({ minutes });
    const newQuery = new URLSearchParams(query);
    newQuery.set("sourceStartDate", time.toFormat("yyyy-MM-dd"));
    newQuery.set("sourceStartTimeInDay", time.toFormat("HH:mm"));
    if (location.pathname === `/workspace/calendar/schedule/event-in-day/new`) {
      navigate(`/workspace/calendar/schedule/event-in-day/new?${newQuery}`, {
        replace: true,
      });
    } else if (
      location.pathname.startsWith(`/workspace/calendar/schedule/event-in-day/`)
    ) {
      navigate(`${location.pathname}?${newQuery}`, {
        replace: true,
      });
    } else if (
      location.pathname ===
      `/workspace/calendar/time-event/in-day-block/new-for-inbox-task`
    ) {
      navigate(
        `/workspace/calendar/time-event/in-day-block/new-for-inbox-task?${newQuery}`,
        {
          replace: true,
        }
      );
    } else if (
      location.pathname.startsWith(
        `/workspace/calendar/time-event/in-day-block/`
      )
    ) {
      navigate(`${location.pathname}?${newQuery}`, {
        replace: true,
      });
    } else {
      navigate(`/workspace/calendar/schedule/event-in-day/new?${newQuery}`, {
        replace: true,
      });
    }
  }

  return (
    <Box
      sx={{
        position: "relative",
        flexGrow: 1,
        height: "96rem",
        minWidth: "7rem",
      }}
      ref={wholeColumnRef}
      onDoubleClick={createNewFromDoubleClick}
    >
      {props.today === props.date && (
        <Box
          sx={{
            position: "absolute",
            top: calendarTimeEventInDayStartMinutesToRems(theMinutes),
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

      <TimeEventParamsNewPlaceholder date={props.date} />

      {props.timeEventsInDay.map((entry, index) => (
        <ViewAsCalendarTimeEventInDayCell
          key={index}
          offset={timeBlockOffsetsMap.get(entry.time_event_in_tz.ref_id) || 0}
          startOfDay={startOfDay}
          entry={entry}
        />
      ))}
    </Box>
  );
}

interface ViewAsCalendarTimeEventInDayCellProps {
  offset: number;
  startOfDay: DateTime;
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

  switch (props.entry.time_event_in_tz.namespace) {
    case TimeEventNamespace.SCHEDULE_EVENT_IN_DAY: {
      const scheduleEntry = props.entry.entry as ScheduleInDayEventEntry;

      const startTime = calculateStartTimeForTimeEvent(
        props.entry.time_event_in_tz
      );
      const endTime = calculateEndTimeForTimeEvent(
        props.entry.time_event_in_tz
      );
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
            fontSize: "10px",
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
            minWidth: `calc(7rem - ${props.offset * 0.8}rem - 0.5rem)`,
            width: `calc(100% - ${props.offset * 0.8}rem - 0.5rem)`,
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
                top: "0rem",
                left: "0.1rem",
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
    }

    case TimeEventNamespace.INBOX_TASK: {
      const inboxTaskEntry = props.entry.entry as InboxTaskEntry;

      const startTime = calculateStartTimeForTimeEvent(
        props.entry.time_event_in_tz
      );
      const endTime = calculateEndTimeForTimeEvent(
        props.entry.time_event_in_tz
      );

      const minutesSinceStartOfDay = startTime
        .diff(props.startOfDay)
        .as("minutes");

      const clippedName = clipTimeEventInDayNameToWhatFits(
        startTime,
        endTime,
        inboxTaskEntry.inbox_task.name,
        theme.typography.htmlFontSize,
        containerWidth,
        minutesSinceStartOfDay,
        props.entry.time_event_in_tz.duration_mins
      );

      return (
        <Box
          ref={containerRef}
          sx={{
            fontSize: "10px",
            position: "absolute",
            top: calendarTimeEventInDayStartMinutesToRems(
              minutesSinceStartOfDay
            ),
            height: calendarTimeEventInDayDurationToRems(
              minutesSinceStartOfDay,
              props.entry.time_event_in_tz.duration_mins
            ),
            backgroundColor: scheduleStreamColorHex(
              INBOX_TASK_TIME_EVENT_COLOR
            ),
            borderRadius: "0.25rem",
            border: `1px solid ${theme.palette.background.paper}`,
            minWidth: `calc(7rem - ${props.offset * 0.8}rem  - 0.5rem)`,
            width: `calc(100% - ${props.offset * 0.8}rem - 0.5rem)`,
            marginLeft: `${props.offset * 0.8}rem`,
            zIndex: props.offset,
          }}
        >
          <EntityLink
            key={`time-event-in-day-block-${props.entry.time_event_in_tz.ref_id}`}
            to={`/workspace/calendar/time-event/in-day-block/${props.entry.time_event_in_tz.ref_id}?${query}`}
          >
            <Box
              sx={{
                position: "absolute",
                width: "100%",
                height: "100%",
                top: "0rem",
                left: "0.1rem",
                overflow: "hidden",
              }}
            >
              <EntityNameComponent
                name={clippedName}
                color={scheduleStreamColorContrastingHex(
                  INBOX_TASK_TIME_EVENT_COLOR
                )}
              />
            </Box>
          </EntityLink>
        </Box>
      );
    }

    default:
      throw new Error("Unkown namespace");
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
        zIndex: theme.zIndex.appBar + 20,
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
        to={`/workspace/calendar${props.calendarLocation}?date=${props.periodStart}&period=${props.period}&view=calendar`}
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

function ViewAsCalendarEmptyCell(props: PropsWithChildren) {
  return (
    <Box sx={{ minWidth: "3.5rem", dispaly: "flex", flexDirection: "column" }}>
      {props.children}
    </Box>
  );
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
  for (const entry of props.entries.vacation_entries) {
    combinedTimeEventFullDays.push({
      time_event: entry.time_event,
      entry: entry,
    });
  }

  const combinedTimeEventInDay: Array<CombinedTimeEventInDayEntry> = [];
  for (const entry of props.entries.schedule_event_in_day_entries) {
    combinedTimeEventInDay.push({
      time_event_in_tz: timeEventInDayBlockToTimezone(
        entry.time_event,
        props.timezone
      ),
      entry: entry,
    });
  }
  for (const entry of props.entries.inbox_task_entries) {
    for (const timeEvent of entry.time_events) {
      combinedTimeEventInDay.push({
        time_event_in_tz: timeEventInDayBlockToTimezone(
          timeEvent,
          props.timezone
        ),
        entry: entry,
      });
    }
  }

  const periodStartDate = DateTime.fromISO(props.periodStartDate);
  const periodEndDate = DateTime.fromISO(props.periodEndDate);
  const daysToProcess = allDaysBetween(
    props.periodStartDate,
    props.periodEndDate
  );
  const partitionedCombinedTimeEventFullDays =
    combinedTimeEventFullDayEntryPartionByDay(combinedTimeEventFullDays);
  const partitionedCombinedTimeEventInDay =
    combinedTimeEventInDayEntryPartionByDay(combinedTimeEventInDay);

  return (
    <>
      {props.period === RecurringTaskPeriod.DAILY && (
        <Typography variant="h5">
          Viewing {periodStartDate.toFormat("dd MMM yyyy")}
        </Typography>
      )}
      {props.period === RecurringTaskPeriod.WEEKLY && (
        <Typography variant="h5">
          Viewing W{periodStartDate.weekNumber} {periodStartDate.year} from{" "}
          {periodStartDate.toFormat("dd MMM")} to{" "}
          {periodEndDate.toFormat("dd MMM")}
        </Typography>
      )}

      <TableContainer component={Paper}>
        <Table sx={{ borderCollapse: "separate", borderSpacing: "0.2rem" }}>
          <TableBody>
            {daysToProcess.map((date) => {
              const partitionFullDays =
                partitionedCombinedTimeEventFullDays[date] || [];
              const partitionInDay =
                partitionedCombinedTimeEventInDay[date] || [];

              if (
                partitionFullDays.length === 0 &&
                partitionInDay.length === 0
              ) {
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
                          {DateTime.fromISO(date).toFormat("MMM-dd")}
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
                          />
                        </TableRow>
                      )}

                      {otherRowsInDay.map((entry, index) => (
                        <TableRow key={index}>
                          <ViewAsScheduleTimeEventInDaysRows entry={entry} />
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
                        />
                      </TableRow>

                      {otherRowsInDay.map((entry, index) => (
                        <TableRow key={index}>
                          <ViewAsScheduleTimeEventInDaysRows entry={entry} />
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
    </>
  );
}

function ViewAsScheduleMonthlyQuarterlyAndYearly(props: ViewAsProps) {
  const isBigScreen = useBigScreen();

  if (props.stats === undefined) {
    throw new Error("Stats are required");
  }

  const periodStartDate = DateTime.fromISO(props.periodStartDate);

  return (
    <>
      {props.period === RecurringTaskPeriod.MONTHLY && (
        <Typography variant="h5">
          Viewing {periodStartDate.monthLong} {periodStartDate.year}
        </Typography>
      )}
      {props.period === RecurringTaskPeriod.QUARTERLY && (
        <Typography variant="h5">
          Viewing {monthToQuarter(periodStartDate.month)} {periodStartDate.year}
        </Typography>
      )}
      {props.period === RecurringTaskPeriod.YEARLY && (
        <Typography variant="h5">Viewing {periodStartDate.year}</Typography>
      )}
      <TableContainer component={Paper}>
        <Table sx={{ borderCollapse: "separate", borderSpacing: "0.2rem" }}>
          <TableBody>
            {props.stats.per_subperiod.map((stats, index) => {
              return (
                <TableRow key={index}>
                  <ViewAsScheduleDateCell isbigscreen={isBigScreen.toString()}>
                    {DateTime.fromISO(stats.period_start_date).toFormat(props.period === RecurringTaskPeriod.YEARLY ? "MMM" : "MMM-dd")}
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
    </>
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
    case TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK: {
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
    }

    case TimeEventNamespace.PERSON_BIRTHDAY: {
      const fullDaysEntry = props.entry.entry as PersonEntry;
      return (
        <React.Fragment>
          <ViewAsScheduleTimeCell isbigscreen={isBigScreen.toString()}>
            [All Day]
          </ViewAsScheduleTimeCell>

          <ViewAsScheduleEventCell
            color={scheduleStreamColorHex(BIRTHDAY_TIME_EVENT_COLOR)}
            isbigscreen={isBigScreen.toString()}
            height="0.25rem"
          >
            <EntityLink
              light
              key={`schedule-event-full-days-${fullDaysEntry.birthday_time_event.ref_id}`}
              to={`/workspace/calendar/time-event/full-days-block/${fullDaysEntry.birthday_time_event.ref_id}?${query}`}
            >
              <EntityNameComponent
                name={`👨 ${birthdayTimeEventName(
                  fullDaysEntry.birthday_time_event,
                  fullDaysEntry.person
                )}`}
                color={scheduleStreamColorContrastingHex(
                  BIRTHDAY_TIME_EVENT_COLOR
                )}
              />
            </EntityLink>
          </ViewAsScheduleEventCell>
        </React.Fragment>
      );
    }

    case TimeEventNamespace.VACATION: {
      const fullDaysEntry = props.entry.entry as VacationEntry;
      return (
        <React.Fragment>
          <ViewAsScheduleTimeCell isbigscreen={isBigScreen.toString()}>
            [All Day]
          </ViewAsScheduleTimeCell>

          <ViewAsScheduleEventCell
            color={scheduleStreamColorHex(VACATION_TIME_EVENT_COLOR)}
            isbigscreen={isBigScreen.toString()}
            height="0.25rem"
          >
            <EntityLink
              light
              key={`schedule-event-full-days-${fullDaysEntry.time_event.ref_id}`}
              to={`/workspace/calendar/time-event/full-days-block/${fullDaysEntry.time_event.ref_id}?${query}`}
            >
              <EntityNameComponent
                name={`🌴 ${fullDaysEntry.vacation.name}`}
                color={scheduleStreamColorContrastingHex(
                  VACATION_TIME_EVENT_COLOR
                )}
              />
            </EntityLink>
          </ViewAsScheduleEventCell>
        </React.Fragment>
      );
    }

    default:
      throw new Error("Unkown namespace");
  }
}

interface ViewAsScheduleTimeEventInDaysRowsProps {
  entry: CombinedTimeEventInDayEntry;
}

function ViewAsScheduleTimeEventInDaysRows(
  props: ViewAsScheduleTimeEventInDaysRowsProps
) {
  const [query] = useSearchParams();
  const isBigScreen = useBigScreen();

  const startTime = calculateStartTimeForTimeEvent(
    props.entry.time_event_in_tz
  );
  const endTime = calculateEndTimeForTimeEvent(props.entry.time_event_in_tz);

  switch (props.entry.time_event_in_tz.namespace) {
    case TimeEventNamespace.SCHEDULE_EVENT_IN_DAY: {
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
              props.entry.time_event_in_tz.duration_mins
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
    }

    case TimeEventNamespace.INBOX_TASK: {
      const inboxTaskEntry = props.entry.entry as InboxTaskEntry;
      return (
        <React.Fragment>
          <ViewAsScheduleTimeCell isbigscreen={isBigScreen.toString()}>
            [{startTime.toFormat("HH:mm")} - {endTime.toFormat("HH:mm")}]
          </ViewAsScheduleTimeCell>

          <ViewAsScheduleEventCell
            color={scheduleStreamColorHex(INBOX_TASK_TIME_EVENT_COLOR)}
            isbigscreen={isBigScreen.toString()}
            height={scheduleTimeEventInDayDurationToRems(
              props.entry.time_event_in_tz.duration_mins
            )}
          >
            <EntityLink
              light
              key={`time-event-in-day-block-${props.entry.time_event_in_tz.ref_id}`}
              to={`/workspace/calendar/time-event/in-day-block/${props.entry.time_event_in_tz.ref_id}?${query}`}
            >
              <EntityNameComponent
                name={inboxTaskEntry.inbox_task.name}
                color={scheduleStreamColorContrastingHex(
                  INBOX_TASK_TIME_EVENT_COLOR
                )}
              />
            </EntityLink>
          </ViewAsScheduleEventCell>
        </React.Fragment>
      );
    }

    default:
      throw new Error("Unkown namespace");
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
      to={`/workspace/calendar${props.calendarLocation}?date=${props.stats.period_start_date}&period=${props.stats.period}&view=${props.view}`}
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
        <span>
          🌴 {props.stats.vacation_cnt}{" "}
          {!props.showCompact ? "from Vacations" : ""}
        </span>
      </Box>
    </EntityLink>
  );
}

export function computeTimeEventInDayDurationInQuarters(
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
  return Math.max(1, finalDurationInMins / 15);
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

  for (const dateStr in partition) {
    partition[dateStr] = sortTimeEventFullDaysByType(partition[dateStr]);
  }

  return partition;
}

function sortTimeEventFullDaysByType(
  entries: Array<CombinedTimeEventFullDaysEntry>
) {
  return entries.sort((a, b) => {
    if (a.time_event.namespace === b.time_event.namespace) {
      return compareADate(a.time_event.start_date, b.time_event.start_date);
    }

    return compareNamespaceForSortingFullDaysTimeEvents(
      a.time_event.namespace,
      b.time_event.namespace
    );
  });
}

function splitTimeEventInDayEntryIntoPerDayEntries(
  entry: CombinedTimeEventInDayEntry
): {
  day1: CombinedTimeEventInDayEntry;
  day2?: CombinedTimeEventInDayEntry;
  day3?: CombinedTimeEventInDayEntry;
} {
  const startTime = calculateStartTimeForTimeEvent(entry.time_event_in_tz);
  const endTime = calculateEndTimeForTimeEvent(entry.time_event_in_tz);
  const diffInDays = endTime
    .startOf("day")
    .diff(startTime.startOf("day"), "days").days;

  if (diffInDays === 0) {
    // Here we have only one day.
    return {
      day1: entry,
    };
  } else if (diffInDays === 1) {
    // Here we have two days.
    const day1TimeEvent = {
      ...entry.time_event_in_tz,
      duration_mins:
        -1 *
        startTime.diff(startTime.set({ hour: 23, minute: 59 })).as("minutes"),
    };
    const day2TimeEvent = {
      ...entry.time_event_in_tz,
      start_date: endTime.toISODate(),
      start_time_in_day: "00:00",
      duration_mins: endTime
        .diff(endTime.set({ hour: 0, minute: 0 }))
        .as("minutes"),
    };

    return {
      day1: {
        time_event_in_tz: day1TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day1TimeEvent,
        },
      },
      day2: {
        time_event_in_tz: day2TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day2TimeEvent,
        },
      },
    };
  } else if (diffInDays === 2) {
    // Here we have three days.
    const day1TimeEvent = {
      ...entry.time_event_in_tz,
      duration_mins:
        -1 *
        startTime.diff(startTime.set({ hour: 23, minute: 59 })).as("minutes"),
    };
    const day2TimeEvent = {
      ...entry.time_event_in_tz,
      start_date: startTime.plus({ days: 1 }).toISODate(),
      start_time_in_day: "00:00",
      duration_mins: 24 * 60,
    };
    const day3TimeEvent = {
      ...entry.time_event_in_tz,
      start_date: endTime.toISODate(),
      start_time_in_day: "00:00",
      duration_mins: endTime
        .diff(endTime.set({ hour: 0, minute: 0 }))
        .as("minutes"),
    };

    return {
      day1: {
        time_event_in_tz: day1TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day1TimeEvent,
        },
      },
      day2: {
        time_event_in_tz: day2TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day2TimeEvent,
        },
      },
      day3: {
        time_event_in_tz: day3TimeEvent,
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
  entries: Array<CombinedTimeEventInDayEntry>
): Record<string, Array<CombinedTimeEventInDayEntry>> {
  const partition: Record<string, Array<CombinedTimeEventInDayEntry>> = {};

  for (const entry of entries) {
    const splitEntries = splitTimeEventInDayEntryIntoPerDayEntries(entry);

    const dateStr = splitEntries.day1.time_event_in_tz.start_date;
    if (partition[dateStr] === undefined) {
      partition[dateStr] = [];
    }
    partition[dateStr].push(splitEntries.day1);

    if (splitEntries.day2) {
      const dateStr = splitEntries.day2.time_event_in_tz.start_date;
      if (partition[dateStr] === undefined) {
        partition[dateStr] = [];
      }
      partition[dateStr].push(splitEntries.day2);
    }

    if (splitEntries.day3) {
      const dateStr = splitEntries.day3.time_event_in_tz.start_date;
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
    const aStartTime = calculateStartTimeForTimeEvent(a.time_event_in_tz);
    const bStartTime = calculateStartTimeForTimeEvent(b.time_event_in_tz);

    if (aStartTime === bStartTime) {
      const aEndTime = calculateEndTimeForTimeEvent(a.time_event_in_tz);
      const bEndTime = calculateEndTimeForTimeEvent(b.time_event_in_tz);
      return aEndTime < bEndTime ? -1 : 1;
    }
    return aStartTime < bStartTime ? -1 : 1;
  });
}

function buildTimeBlockOffsetsMap(
  entries: Array<CombinedTimeEventInDayEntry>,
  startOfDay: DateTime
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
    const startTime = calculateStartTimeForTimeEvent(entry.time_event_in_tz);
    const minutesSinceStartOfDay = startTime.diff(startOfDay).as("minutes");

    const firstCellIdx = Math.floor(minutesSinceStartOfDay / 15);
    const offsetCell = freeOffsetsMap[firstCellIdx];

    if (offsetCell.offset0 === false) {
      offsets.set(entry.time_event_in_tz.ref_id, 0);
      offsetCell.offset0 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event_in_tz.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset0 = true;
      }
      continue;
    } else if (offsetCell.offset1 === false) {
      offsets.set(entry.time_event_in_tz.ref_id, 1);
      offsetCell.offset1 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event_in_tz.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset1 = true;
      }
      continue;
    } else if (offsetCell.offset2 === false) {
      offsets.set(entry.time_event_in_tz.ref_id, 2);
      offsetCell.offset2 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event_in_tz.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset2 = true;
      }
      continue;
    } else if (offsetCell.offset3 === false) {
      offsets.set(entry.time_event_in_tz.ref_id, 3);
      offsetCell.offset3 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event_in_tz.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset3 = true;
      }
      continue;
    } else {
      offsets.set(entry.time_event_in_tz.ref_id, 4);
      offsetCell.offset4 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event_in_tz.duration_mins;
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

function monthToQuarter(month: number): string {
  switch (month) {
    case 1:
    case 2:
    case 3:
      return "Q1";
    case 4:
    case 5:
    case 6:
      return "Q2";
    case 7:
    case 8:
    case 9:
      return "Q3";
    case 10:
    case 11:
    case 12:
      return "Q4";
    default:
      throw new Error("Unexpected month");
  }
}

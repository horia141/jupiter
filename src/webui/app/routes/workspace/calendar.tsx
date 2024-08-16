import type {
  ADate,
  InboxTaskEntry,
  PersonEntry,
  ScheduleFullDaysEventEntry,
  ScheduleInDayEventEntry,
  TimeEventFullDaysBlock,
  TimeEventInDayBlock,
} from "@jupiter/webapi-client";
import {
  RecurringTaskPeriod,
  TimeEventNamespace,
} from "@jupiter/webapi-client";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import {
  Paper,
  styled,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
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
import React, { useContext } from "react";
import { z } from "zod";
import { parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import {
  NavMultipleCompact,
  NavMultipleSpread,
  NavSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { ScheduleStreamColorTag } from "~/components/schedule-stream-color-tag";
import { aDateToDate, allDaysBetween } from "~/logic/domain/adate";
import { periodName } from "~/logic/domain/period";
import { scheduleStreamColorHex } from "~/logic/domain/schedule-stream-color";
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
  });

  return json({
    today: query.today as string,
    period: query.period as RecurringTaskPeriod,
    view: query.view as View,
    periodStartDate: response.period_start_date,
    periodEndDate: response.period_end_date,
    prevPeriodStartDate: response.prev_period_start_date,
    nextPeriodStartDate: response.next_period_start_date,
    scheduleEventInDayEntries: response.schedule_event_in_day_entries,
    scheduleEventFullDayEntries: response.schedule_event_full_days_entries,
    inboxTaskEntries: response.inbox_task_entries,
    personEntries: response.person_entries,
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
                  text: "View Calendar Streams",
                  link: `/workspace/calendar/schedule/stream?${query}`,
                }),
              ],
            }),
            NavMultipleSpread({
              navs: [
                NavSingle({
                  text: "Today",
                  link: `/workspace/calendar${calendarLocation}?today=${DateTime.now().toISODate()}&period=${
                    loaderData.period
                  }&view=${loaderData.view}`,
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
        {loaderData.view === View.CALENDAR && (
          <EntityStack>
            <p>
              For {loaderData.today} and {loaderData.period} and{" "}
              {loaderData.view}
            </p>
          </EntityStack>
        )}

        {loaderData.view === View.SCHEDULE && (
          <ViewAsSchedule
            timezone={topLevelInfo.user.timezone}
            periodStartDate={loaderData.periodStartDate}
            periodEndDate={loaderData.periodEndDate}
            scheduleEventInDayEntries={loaderData.scheduleEventInDayEntries}
            scheduleEventFullDayEntries={loaderData.scheduleEventFullDayEntries}
            inboxTaskEntries={loaderData.inboxTaskEntries}
            personEntries={loaderData.personEntries}
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

interface ViewAsScheduleProps {
  timezone: string;
  periodStartDate: ADate;
  periodEndDate: ADate;
  scheduleEventInDayEntries: Array<ScheduleInDayEventEntry>;
  scheduleEventFullDayEntries: Array<ScheduleFullDaysEventEntry>;
  inboxTaskEntries: Array<InboxTaskEntry>;
  personEntries: Array<PersonEntry>;
}

function ViewAsSchedule(props: ViewAsScheduleProps) {
  const isBigScreen = useBigScreen();
  
  const combinedTimeEventFullDays: Array<CombinedTimeEventFullDaysEntry> = [];
  for (const entry of props.scheduleEventFullDayEntries) {
    combinedTimeEventFullDays.push({
      time_event: entry.time_event,
      entry: entry,
    });
  }
  for (const entry of props.personEntries) {
    combinedTimeEventFullDays.push({
      time_event: entry.birthday_time_event,
      entry: entry,
    });
  }

  const combinedTimeEventInDay: Array<CombinedTimeEventInDayEntry> = [];
  for (const entry of props.scheduleEventInDayEntries) {
    combinedTimeEventInDay.push({
      time_event: entry.time_event,
      entry: entry,
    });
  }
  for (const entry of props.inboxTaskEntries) {
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
    combinedTimeEventFullDayEntryPartionByDay(
      combinedTimeEventFullDays,
      props.periodStartDate,
      props.periodEndDate
    );
  const partitionedCombinedTimeEventInDay =
    combinedTimeEventInDayEntryPartionByDay(
      combinedTimeEventInDay,
      props.periodStartDate,
      props.periodEndDate
    );

  return (
    <TableContainer component={Paper}>
      <Table sx={{borderCollapse: "separate", borderSpacing: "0.2rem"}}>
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

                      <CombinedTimeEventFullDaysRows entry={firstRowFullDays} />
                    </TableRow>

                    {otherRowsFullDays.map((entry, index) => (
                      <TableRow key={index}>
                        <CombinedTimeEventFullDaysRows entry={entry} />
                      </TableRow>
                    ))}

                    {firstRowInDay && (
                      <TableRow>
                        <CombinedTimeEventInDaysRows entry={firstRowInDay} />
                      </TableRow>
                    )}

                    {otherRowsInDay.map((entry, index) => (
                      <TableRow key={index}>
                        <CombinedTimeEventInDaysRows entry={entry} />
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

                      <CombinedTimeEventInDaysRows entry={firstRowInDay} />
                    </TableRow>

                    {otherRowsInDay.map((entry, index) => (
                      <TableRow key={index}>
                        <CombinedTimeEventInDaysRows entry={entry} />
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

function CombinedTimeEventFullDaysRows({
  entry,
}: {
  entry: CombinedTimeEventFullDaysEntry;
}) {
  const [query] = useSearchParams();
  const isBigScreen = useBigScreen();

  switch (entry.time_event.namespace) {
    case TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK:
      const fullDaysEntry = entry.entry as ScheduleFullDaysEventEntry;
      return (
        <React.Fragment>
          <ViewAsScheduleTimeCell isbigscreen={isBigScreen.toString()}>[AllDay]</ViewAsScheduleTimeCell>

          <ViewAsScheduleEventCell 
              color={scheduleStreamColorHex(fullDaysEntry.stream.color)}
              isbigscreen={isBigScreen.toString()}
              height="0.25rem">
            <EntityLink
              light
              key={`schedule-event-full-days-${fullDaysEntry.event.ref_id}`}
              to={`/workspace/calendar/schedule/event-full-days/${fullDaysEntry.event.ref_id}?${query}`}
            >
              <EntityNameComponent name={fullDaysEntry.event.name} />
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

function timeEventInDayDurationToRems(durationMins: number): string {
  const durationHours = 0.5 + Math.floor(durationMins / 30);
  return `${durationHours}rem`;
}

function CombinedTimeEventInDaysRows({
  entry,
}: {
  entry: CombinedTimeEventInDayEntry;
}) {
  const [query] = useSearchParams();
  const isBigScreen = useBigScreen();

  const startTime = DateTime.fromISO(
    `${entry.time_event.start_date}T${entry.time_event.start_time_in_day}`,
    { zone: "UTC" }
  );
  const endTime = startTime.plus({
    minutes: entry.time_event.duration_mins,
  });

  switch (entry.time_event.namespace) {
    case TimeEventNamespace.SCHEDULE_EVENT_IN_DAY:
      const scheduleEntry = entry.entry as ScheduleInDayEventEntry;
      return (
        <React.Fragment>
          <ViewAsScheduleTimeCell isbigscreen={isBigScreen.toString()}>
            [{startTime.toFormat("HH:mm")} - {endTime.toFormat("HH:mm")}]
          </ViewAsScheduleTimeCell>

          <ViewAsScheduleEventCell 
              color={scheduleStreamColorHex(scheduleEntry.stream.color)}
              isbigscreen={isBigScreen.toString()}
              height={timeEventInDayDurationToRems(scheduleEntry.time_event.duration_mins)}>
            <EntityLink
              light
              key={`schedule-event-in-day-${scheduleEntry.event.ref_id}`}
              to={`/workspace/calendar/schedule/event-in-day/${scheduleEntry.event.ref_id}?${query}`}
            >
              <EntityNameComponent name={scheduleEntry.event.name} />
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

const ViewAsScheduleDateCell = styled(TableCell)<ViewAsScheduleDateCellProps>(({isbigscreen}) => ({
  verticalAlign: "top",
  padding: "0.25rem",
  width: isbigscreen === "true" ? "15%" : "25%"
}));

interface ViewAsScheduleTimeCellProps {
  isbigscreen: string;
}

const ViewAsScheduleTimeCell = styled(TableCell)<ViewAsScheduleTimeCellProps>(({isbigscreen}) => ({
  verticalAlign: "top",
  padding: "0.25rem",
  width: isbigscreen === "true" ? "15%" : "30%"
}));

interface ViewAsScheduleEventCellProps {
  isbigscreen: string;
  color: string;
  height: string;
}

const ViewAsScheduleEventCell = styled(TableCell)<ViewAsScheduleEventCellProps>(({isbigscreen, color, height}) => ({
  verticalAlign: "top",
  backgroundColor: color,
  padding: "0.25rem",
  paddingLeft: "0.5rem",
  paddingBottom: height,
  borderRadius: "0.25rem",            
}));

interface CombinedTimeEventFullDaysEntry {
  time_event: TimeEventFullDaysBlock;
  entry: ScheduleFullDaysEventEntry | PersonEntry;
}

interface CombinedTimeEventInDayEntry {
  time_event: TimeEventInDayBlock;
  entry: ScheduleInDayEventEntry | InboxTaskEntry;
}

function combinedTimeEventFullDayEntryPartionByDay(
  entries: Array<CombinedTimeEventFullDaysEntry>,
  periodStartDate: ADate,
  periodEndDate: ADate
): Record<string, Array<CombinedTimeEventFullDaysEntry>> {
  const partition: Record<string, Array<CombinedTimeEventFullDaysEntry>> = {};
  const startDate = aDateToDate(periodStartDate);
  const endDate = aDateToDate(periodEndDate);

  for (const entry of entries) {
    const firstDate = aDateToDate(entry.time_event.start_date);
    for (let idx = 0; idx < entry.time_event.duration_days; idx++) {
      const date = firstDate.plus({ days: idx });
      if (date < startDate || date > endDate) {
        continue;
      }

      const dateStr = date.toISODate();
      if (partition[dateStr] === undefined) {
        partition[dateStr] = [];
      }
      partition[dateStr].push(entry);
    }
  }

  return partition;
}

function combinedTimeEventInDayEntryPartionByDay(
  entries: Array<CombinedTimeEventInDayEntry>,
  periodStartDate: ADate,
  periodEndDate: ADate
): Record<string, Array<CombinedTimeEventInDayEntry>> {
  const partition: Record<string, Array<CombinedTimeEventInDayEntry>> = {};
  const startDate = aDateToDate(periodStartDate);
  const endDate = aDateToDate(periodEndDate);

  for (const entry of entries) {
    const date = aDateToDate(entry.time_event.start_date);
    if (date < startDate || date > endDate) {
      continue;
    }

    const dateStr = date.toISODate();
    if (partition[dateStr] === undefined) {
      partition[dateStr] = [];
    }
    partition[dateStr].push(entry);
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

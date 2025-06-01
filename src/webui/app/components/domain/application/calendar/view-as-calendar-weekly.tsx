import { DateTime } from "luxon";
import { useState } from "react";
import { Box, Typography } from "@mui/material";

import {
  combinedTimeEventFullDayEntryPartionByDay,
  CombinedTimeEventInDayEntry,
  timeEventInDayBlockToTimezone,
  CombinedTimeEventFullDaysEntry,
  combinedTimeEventInDayEntryPartionByDay,
} from "~/logic/domain/time-event";
import { useBigScreen } from "~/rendering/use-big-screen";
import { allDaysBetween } from "~/logic/domain/adate";
import {
  MAX_VISIBLE_TIME_EVENT_FULL_DAYS,
  ViewAsCalendarDateHeader,
  ViewAsCalendarDaysAndFullDaysContiner,
  ViewAsCalendarEmptyCell,
  ViewAsCalendarInDayContainer,
  ViewAsCalendarLeftColumn,
  ViewAsCalendarMoreButton,
  ViewAsCalendarRightColumn,
  ViewAsCalendarTimeEventFullDaysColumn,
  ViewAsCalendarTimeEventInDayColumn,
  ViewAsProps,
} from "~/components/domain/application/calendar/shared";

export function ViewAsCalendarWeekly(props: ViewAsProps) {
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
        props.timezone,
      ),
      entry: entry,
    });
  }
  for (const entry of props.entries.inbox_task_entries) {
    for (const timeEvent of entry.time_events) {
      combinedTimeEventInDay.push({
        time_event_in_tz: timeEventInDayBlockToTimezone(
          timeEvent,
          props.timezone,
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
      (entries) => entries.length,
    ),
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
              isAdding={props.isAdding}
            />
          ))}

          <ViewAsCalendarEmptyCell />
        </Box>
      </ViewAsCalendarDaysAndFullDaysContiner>

      <ViewAsCalendarInDayContainer>
        <ViewAsCalendarLeftColumn
          rightNow={props.rightNow}
          showOnlyFromRightNowIfDaily={props.showOnlyFromRightNowIfDaily}
        />

        {allDays.map((date, idx) => (
          <ViewAsCalendarTimeEventInDayColumn
            daysToTheLeft={allDays.length - idx - 1}
            key={idx}
            rightNow={props.rightNow}
            today={props.today}
            timezone={props.timezone}
            date={date}
            timeEventsInDay={partitionedCombinedTimeEventInDay[date] || []}
            isAdding={props.isAdding}
            showOnlyFromRightNowIfDaily={props.showOnlyFromRightNowIfDaily}
          />
        ))}

        <ViewAsCalendarRightColumn
          rightNow={props.rightNow}
          showOnlyFromRightNowIfDaily={props.showOnlyFromRightNowIfDaily}
        />
      </ViewAsCalendarInDayContainer>
    </Box>
  );
}

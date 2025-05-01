import { DateTime } from "luxon";
import { useState } from "react";
import { Box, Typography } from "@mui/material";

import { useBigScreen } from "~/rendering/use-big-screen";
import {
  combinedTimeEventFullDayEntryPartionByDay,
  CombinedTimeEventInDayEntry,
  timeEventInDayBlockToTimezone,
  CombinedTimeEventFullDaysEntry,
  combinedTimeEventInDayEntryPartionByDay,
} from "~/logic/domain/time-event";

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
} from "./shared";

export function ViewAsCalendarDaily(props: ViewAsProps) {
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
            isAdding={props.isAdding}
          />

          <ViewAsCalendarEmptyCell />
        </Box>
      </ViewAsCalendarDaysAndFullDaysContiner>

      <ViewAsCalendarInDayContainer>
        <ViewAsCalendarLeftColumn />
        <ViewAsCalendarTimeEventInDayColumn
          daysToTheLeft={0}
          rightNow={props.rightNow}
          today={props.today}
          timezone={props.timezone}
          date={props.periodStartDate}
          timeEventsInDay={thePartitionInDay}
          isAdding={props.isAdding}
        />
        <ViewAsCalendarRightColumn />
      </ViewAsCalendarInDayContainer>
    </Box>
  );
}

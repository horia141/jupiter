import {
  Paper,
  Table,
  TableCell,
  TableBody,
  TableContainer,
  TableRow,
  Typography,
} from "@mui/material";
import { DateTime } from "luxon";
import { RecurringTaskPeriod } from "@jupiter/webapi-client";
import { Fragment } from "react";

import { useBigScreen } from "~/rendering/use-big-screen";
import type { ViewAsProps } from "~/components/domain/application/calendar/shared";
import {
  ViewAsScheduleTimeEventFullDaysRows,
  ViewAsScheduleTimeEventInDaysRows,
} from "~/components/domain/application/calendar/shared";
import {
  calculateStartTimeForTimeEvent,
  combinedTimeEventFullDayEntryPartionByDay,
  CombinedTimeEventFullDaysEntry,
  CombinedTimeEventInDayEntry,
  combinedTimeEventInDayEntryPartionByDay,
  timeEventInDayBlockToTimezone,
} from "~/logic/domain/time-event";
import { allDaysBetween } from "~/logic/domain/adate";

export function ViewAsScheduleDailyAndWeekly(props: ViewAsProps) {
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
    if (
      props.showOnlyFromRightNowIfDaily &&
      calculateStartTimeForTimeEvent(entry.time_event) < props.rightNow
    ) {
      continue;
    }

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
      if (
        props.showOnlyFromRightNowIfDaily &&
        calculateStartTimeForTimeEvent(timeEvent) < props.rightNow
      ) {
        continue;
      }

      combinedTimeEventInDay.push({
        time_event_in_tz: timeEventInDayBlockToTimezone(
          timeEvent,
          props.timezone,
        ),
        entry: entry,
      });
    }
  }

  const periodStartDate = DateTime.fromISO(props.periodStartDate);
  const periodEndDate = DateTime.fromISO(props.periodEndDate);
  const daysToProcess = allDaysBetween(
    props.periodStartDate,
    props.periodEndDate,
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
                return <Fragment key={date}></Fragment>;
              }

              const firstRowFullDays = partitionFullDays[0];
              const otherRowsFullDays = partitionFullDays.slice(1);
              const firstRowInDay = partitionInDay[0];
              const otherRowsInDay = partitionInDay.slice(1);

              return (
                <Fragment key={date}>
                  {firstRowFullDays && (
                    <>
                      <TableRow>
                        {props.period === RecurringTaskPeriod.WEEKLY && (
                          <TableCell
                            rowSpan={
                              partitionFullDays.length + partitionInDay.length
                            }
                            sx={{
                              padding: "0.25rem",
                              width: isBigScreen ? "15%" : "25%",
                            }}
                          >
                            {isBigScreen
                              ? DateTime.fromISO(date).toFormat("MMM-dd")
                              : DateTime.fromISO(date).toFormat("dd MMM")}
                          </TableCell>
                        )}

                        <ViewAsScheduleTimeEventFullDaysRows
                          period={props.period}
                          entry={firstRowFullDays}
                          isAdding={props.isAdding}
                        />
                      </TableRow>

                      {otherRowsFullDays.map((entry, index) => (
                        <TableRow key={index}>
                          <ViewAsScheduleTimeEventFullDaysRows
                            period={props.period}
                            entry={entry}
                            isAdding={props.isAdding}
                          />
                        </TableRow>
                      ))}

                      {firstRowInDay && (
                        <TableRow>
                          <ViewAsScheduleTimeEventInDaysRows
                            period={props.period}
                            entry={firstRowInDay}
                            isAdding={props.isAdding}
                          />
                        </TableRow>
                      )}

                      {otherRowsInDay.map((entry, index) => (
                        <TableRow key={index}>
                          <ViewAsScheduleTimeEventInDaysRows
                            period={props.period}
                            entry={entry}
                            isAdding={props.isAdding}
                          />
                        </TableRow>
                      ))}
                    </>
                  )}

                  {firstRowFullDays === undefined && firstRowInDay && (
                    <>
                      <TableRow>
                        {props.period === RecurringTaskPeriod.WEEKLY && (
                          <TableCell
                            rowSpan={partitionInDay.length}
                            sx={{
                              verticalAlign: "top",
                              padding: "0.25rem",
                              width: isBigScreen ? "15%" : "25%",
                            }}
                          >
                            {isBigScreen
                              ? DateTime.fromISO(date).toFormat("MMM-dd")
                              : DateTime.fromISO(date).toFormat("dd MMM")}
                          </TableCell>
                        )}

                        <ViewAsScheduleTimeEventInDaysRows
                          period={props.period}
                          entry={firstRowInDay}
                          isAdding={props.isAdding}
                        />
                      </TableRow>

                      {otherRowsInDay.map((entry, index) => (
                        <TableRow key={index}>
                          <ViewAsScheduleTimeEventInDaysRows
                            period={props.period}
                            entry={entry}
                            isAdding={props.isAdding}
                          />
                        </TableRow>
                      ))}
                    </>
                  )}
                </Fragment>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
}

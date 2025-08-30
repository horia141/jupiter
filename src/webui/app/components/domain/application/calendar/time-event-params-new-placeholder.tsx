import type { ADate } from "@jupiter/webapi-client";
import { Box } from "@mui/material";
import { useSearchParams } from "@remix-run/react";

import {
  calculateStartTimeFromBlockParams,
  calendarTimeEventInDayDurationToRems,
  calendarTimeEventInDayStartMinutesToRems,
} from "~/logic/domain/time-event";

interface TimeEventParamsNewPlaceholderParams {
  daysToTheLeft: number;
  date: ADate;
  deltaHour: number;
}

export function TimeEventParamsNewPlaceholder(
  props: TimeEventParamsNewPlaceholderParams,
) {
  const [query] = useSearchParams();

  const sourceStartDate = query.get("sourceStartDate");
  const sourceStartTimeInDay = query.get("sourceStartTimeInDay");
  const sourceDurationMins = query.get("sourceDurationMins");

  if (!sourceStartDate || !sourceStartTimeInDay || !sourceDurationMins) {
    return null;
  }

  const sourceDurationMinsInt = parseInt(sourceDurationMins, 10);

  if (props.date !== sourceStartDate) {
    return null;
  }

  const startTime = calculateStartTimeFromBlockParams({
    startDate: sourceStartDate,
    startTimeInDay: sourceStartTimeInDay,
  });
  const minutesSinceStartOfDay = startTime
    .diff(startTime.startOf("day"))
    .as("minutes");

  const endTime = startTime.plus({ minutes: sourceDurationMinsInt });
  const endOfDay = startTime.endOf("day");
  const overflowMinutes = endTime.diff(endOfDay, "minutes").minutes;

  return (
    <>
      <Box
        sx={{
          position: "absolute",
          top: calendarTimeEventInDayStartMinutesToRems(
            minutesSinceStartOfDay,
            props.deltaHour,
          ),
          height: calendarTimeEventInDayDurationToRems(
            minutesSinceStartOfDay,
            overflowMinutes > 0
              ? sourceDurationMinsInt - overflowMinutes
              : sourceDurationMinsInt,
          ),
          backgroundColor: "gray",
          opacity: 0.5,
          borderRadius: "0.25rem",
          border: "1px solid black",
          minWidth: "calc(7rem - 0.5rem)",
          width: "calc(100% - 0.5rem)",
          zIndex: 10,
        }}
      ></Box>
      {overflowMinutes > 0 && props.daysToTheLeft > 0 && (
        <Box
          sx={{
            position: "absolute",
            top: 0,
            left: "100%",
            height: calendarTimeEventInDayDurationToRems(0, overflowMinutes),
            backgroundColor: "gray",
            opacity: 0.5,
            borderRadius: "0.25rem",
            border: "1px solid black",
            minWidth: "calc(7rem - 0.5rem)",
            width: "calc(100% - 0.5rem)",
            zIndex: 10,
          }}
        ></Box>
      )}
      {overflowMinutes > 24 * 60 && props.daysToTheLeft > 1 && (
        <Box
          sx={{
            position: "absolute",
            top: 0,
            left: "200%",
            height: calendarTimeEventInDayDurationToRems(
              0,
              overflowMinutes - 24 * 60,
            ),
            backgroundColor: "gray",
            opacity: 0.5,
            borderRadius: "0.25rem",
            border: "1px solid black",
            minWidth: "calc(7rem - 0.5rem)",
            width: "calc(100% - 0.5rem)",
            zIndex: 10,
          }}
        ></Box>
      )}
    </>
  );
}

import type { ADate } from "@jupiter/webapi-client";
import { Box } from "@mui/material";
import { useSearchParams } from "@remix-run/react";
import {
  calculateStartTimeFromBlockParams,
  calendarTimeEventInDayDurationToRems,
  calendarTimeEventInDayStartMinutesToRems,
} from "~/logic/domain/time-event";

interface TimeEventParamsNewPlaceholderParams {
  date: ADate;
}

export function TimeEventParamsNewPlaceholder(
  props: TimeEventParamsNewPlaceholderParams
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

  return (
    <Box
      sx={{
        position: "absolute",
        top: calendarTimeEventInDayStartMinutesToRems(minutesSinceStartOfDay),
        height: calendarTimeEventInDayDurationToRems(
          minutesSinceStartOfDay,
          sourceDurationMinsInt
        ),
        backgroundColor: "gray",
        opacity: 0.5,
        borderRadius: "0.25rem",
        border: "1px solid black",
        minWidth: "7rem",
        width: "100%",
        zIndex: 10,
      }}
    ></Box>
  );
}

import { Box, Typography } from "@mui/material";
import { DateTime } from "luxon";

import { useBigScreen } from "~/rendering/use-big-screen";

import type { ViewAsProps } from "./shared";
import { ViewAsCalendarStatsCell } from "./shared";

export function ViewAsCalendarMonthly(props: ViewAsProps) {
  const isBigScreen = useBigScreen();

  if (props.stats === undefined) {
    throw new Error("Stats are required");
  }

  const periodStartDate = DateTime.fromISO(props.periodStartDate);
  const daysInMonth = periodStartDate.daysInMonth;
  if (daysInMonth === undefined) {
    throw new Error("Could not determine days in month");
  }

  const days = Array.from({ length: daysInMonth }, (_, i) =>
    periodStartDate.startOf("month").plus({ days: i }),
  );

  return (
    <>
      <Typography variant="h5">
        Viewing {periodStartDate.toFormat("MMM yyyy")}
      </Typography>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "3rem 1fr 1fr 1fr 1fr 1fr 1fr 1fr",
          gridTemplateRows: "auto",
          gridGap: "0.25rem",
        }}
      >
        <Box sx={{ gridRowStart: 1, gridColumnStart: 1 }}>Day</Box>
        <Box sx={{ gridRowStart: 1, gridColumnStart: 2 }}>Mon</Box>
        <Box sx={{ gridRowStart: 1, gridColumnStart: 3 }}>Tue</Box>
        <Box sx={{ gridRowStart: 1, gridColumnStart: 4 }}>Wed</Box>
        <Box sx={{ gridRowStart: 1, gridColumnStart: 5 }}>Thu</Box>
        <Box sx={{ gridRowStart: 1, gridColumnStart: 6 }}>Fri</Box>
        <Box sx={{ gridRowStart: 1, gridColumnStart: 7 }}>Sat</Box>
        <Box sx={{ gridRowStart: 1, gridColumnStart: 8 }}>Sun</Box>

        {days.map((day, idx) => {
          const weekDay = day.weekday;
          const weekNumber = day.weekNumber;
          const monthStartWeekNumber =
            periodStartDate.startOf("month").weekNumber;
          const weekOffset = weekNumber - monthStartWeekNumber;

          return (
            <Box
              key={idx}
              sx={{
                gridRowStart: weekOffset + 2,
                gridColumnStart: weekDay === 7 ? 8 : weekDay + 1,
              }}
            >
              <ViewAsCalendarStatsCell
                label={day.toFormat("d")}
                forceColumn={isBigScreen}
                showCompact={!isBigScreen}
                stats={
                  props.stats!.per_subperiod.find(
                    (s) => s.period_start_date === day.toISODate(),
                  )!
                }
                calendarLocation={props.calendarLocation}
              />
            </Box>
          );
        })}
      </Box>
    </>
  );
}

import { Box, Typography } from "@mui/material";
import { DateTime } from "luxon";
import { RecurringTaskPeriod } from "@jupiter/webapi-client";

import type { ViewAsProps } from "~/components/domain/application/calendar/shared";
import {
  ViewAsCalendarGoToCell,
  ViewAsCalendarStatsCell,
} from "~/components/domain/application/calendar/shared";

function monthToQuarter(month: number): string {
  if (month <= 3) return "Q1";
  if (month <= 6) return "Q2";
  if (month <= 9) return "Q3";
  return "Q4";
}

export function ViewAsCalendarQuarterly(props: ViewAsProps) {
  if (props.stats === undefined) {
    throw new Error("Stats are required");
  }

  const periodStartDate = DateTime.fromISO(props.periodStartDate);
  const months = Array.from({ length: 3 }, (_, i) =>
    periodStartDate.startOf("quarter").plus({ months: i }),
  );

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
          const monthShort = month.toFormat("MMM");
          const monthDate = month.toISODate();
          if (monthDate === null) {
            throw new Error("Could not format month date");
          }

          return (
            <Box
              key={idx}
              sx={{
                gridRowStart: month.month - periodStartDate.month + 2,
                gridColumnStart: 1,
              }}
            >
              <ViewAsCalendarGoToCell
                label={monthShort}
                period={RecurringTaskPeriod.MONTHLY}
                periodStart={monthDate}
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

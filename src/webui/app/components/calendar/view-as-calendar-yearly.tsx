import { Box, Typography } from "@mui/material";
import { DateTime } from "luxon";
import { RecurringTaskPeriod } from "@jupiter/webapi-client";

import { useBigScreen } from "~/rendering/use-big-screen";

import type { ViewAsProps } from "./shared";
import { ViewAsCalendarGoToCell, ViewAsCalendarStatsCell } from "./shared";

export function ViewAsCalendarYearly(props: ViewAsProps) {
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
                (s) => s.period_start_date === `${periodStartDate.year}-01-01`,
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
                (s) => s.period_start_date === `${periodStartDate.year}-02-01`,
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
                (s) => s.period_start_date === `${periodStartDate.year}-03-01`,
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
                (s) => s.period_start_date === `${periodStartDate.year}-04-01`,
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
                (s) => s.period_start_date === `${periodStartDate.year}-05-01`,
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
                (s) => s.period_start_date === `${periodStartDate.year}-06-01`,
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
                (s) => s.period_start_date === `${periodStartDate.year}-07-01`,
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
                (s) => s.period_start_date === `${periodStartDate.year}-08-01`,
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
                (s) => s.period_start_date === `${periodStartDate.year}-09-01`,
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
                (s) => s.period_start_date === `${periodStartDate.year}-10-01`,
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
                (s) => s.period_start_date === `${periodStartDate.year}-11-01`,
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
                (s) => s.period_start_date === `${periodStartDate.year}-12-01`,
              )!
            }
            calendarLocation={props.calendarLocation}
          />
        </Box>
      </Box>
    </>
  );
}

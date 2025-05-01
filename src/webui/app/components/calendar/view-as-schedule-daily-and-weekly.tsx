import {
  Table,
  TableBody,
  TableContainer,
  TableRow,
  Typography,
} from "@mui/material";
import { DateTime } from "luxon";
import { RecurringTaskPeriod } from "@jupiter/webapi-client";

import { useBigScreen } from "~/rendering/use-big-screen";

import type { ViewAsProps } from "./shared";
import {
  ViewAsScheduleDateCell,
  ViewAsScheduleContentCell,
  ViewAsStatsPerSubperiod,
  View,
} from "./shared";

export function ViewAsScheduleDailyAndWeekly(props: ViewAsProps) {
  const isBigScreen = useBigScreen();

  if (props.stats === undefined) {
    throw new Error("Stats are required");
  }

  const periodStartDate = DateTime.fromISO(props.periodStartDate);

  return (
    <>
      {props.period === RecurringTaskPeriod.DAILY && (
        <Typography variant="h5">
          Viewing {periodStartDate.toFormat("MMM dd, yyyy")}
        </Typography>
      )}
      {props.period === RecurringTaskPeriod.WEEKLY && (
        <Typography variant="h5">
          Viewing Week {periodStartDate.weekNumber} of {periodStartDate.year}
        </Typography>
      )}
      <TableContainer>
        <Table>
          <TableBody>
            {props.stats.per_subperiod.map((stats, index) => {
              return (
                <TableRow key={index}>
                  <ViewAsScheduleDateCell isbigscreen={isBigScreen.toString()}>
                    {DateTime.fromISO(stats.period_start_date).toFormat(
                      props.period === RecurringTaskPeriod.DAILY
                        ? "EEE, MMM dd"
                        : "EEE, MMM dd",
                    )}
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

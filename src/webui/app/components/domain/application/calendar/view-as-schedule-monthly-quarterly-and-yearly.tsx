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
import type { ViewAsProps } from "~/components/domain/application/calendar/shared";
import {
  ViewAsScheduleDateCell,
  ViewAsScheduleContentCell,
  ViewAsStatsPerSubperiod,
  View,
} from "~/components/domain/application/calendar/shared";

function monthToQuarter(month: number): string {
  if (month <= 3) return "Q1";
  if (month <= 6) return "Q2";
  if (month <= 9) return "Q3";
  return "Q4";
}

export function ViewAsScheduleMonthlyQuarterlyAndYearly(props: ViewAsProps) {
  const isBigScreen = useBigScreen();

  if (props.stats === undefined) {
    throw new Error("Stats are required");
  }

  const periodStartDate = DateTime.fromISO(props.periodStartDate);

  return (
    <>
      {props.period === RecurringTaskPeriod.MONTHLY && (
        <Typography variant="h5">
          Viewing {periodStartDate.monthLong} {periodStartDate.year}
        </Typography>
      )}
      {props.period === RecurringTaskPeriod.QUARTERLY && (
        <Typography variant="h5">
          Viewing {monthToQuarter(periodStartDate.month)} {periodStartDate.year}
        </Typography>
      )}
      {props.period === RecurringTaskPeriod.YEARLY && (
        <Typography variant="h5">Viewing {periodStartDate.year}</Typography>
      )}
      <TableContainer>
        <Table>
          <TableBody>
            {props.stats.per_subperiod.map((stats, index) => {
              return (
                <TableRow key={index}>
                  <ViewAsScheduleDateCell isbigscreen={isBigScreen.toString()}>
                    {DateTime.fromISO(stats.period_start_date).toFormat(
                      props.period === RecurringTaskPeriod.YEARLY
                        ? "MMM"
                        : "MMM-dd",
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

import {
  ADate,
  Habit,
  HabitStreakMark,
  InboxTaskStatus,
} from "@jupiter/webapi-client";
import { Box, IconButton, Stack, Tooltip, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";
import { PropsWithChildren } from "react";
import ArrowBackIosNewIcon from "@mui/icons-material/ArrowBackIosNew";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import { Link } from "@remix-run/react";

import { aDateToDate, dateToAdate } from "~/logic/domain/adate";
import { DateTime } from "luxon";

interface HabitStreakCalendarProps {
  earliestDate: ADate;
  latestDate: ADate;
  currentToday: ADate;
  habit: Habit;
  streakMarks: HabitStreakMark[];
  noLabel?: boolean;
  label?: string;
  showNav?: boolean;
  getNavUrl?: (earliestDate: ADate, latestDate: ADate) => string;
}

export function HabitStreakCalendar(props: HabitStreakCalendarProps) {
  const earliestDate = aDateToDate(props.earliestDate);
  const latestDate = aDateToDate(props.latestDate);

  const data: Map<string, number> = new Map();
  for (const streakMark of props.streakMarks) {
    data.set(streakMark.date, computeDonenessForStreakMark(streakMark));
  }

  return (
    <StyledDiv>
      <Stack direction="row" sx={{ alignSelf: "center" }}>
        {props.showNav && props.getNavUrl && (
          <NavBefore
            to={props.getNavUrl(
              dateToAdate(earliestDate.minus({ days: 28 })),
              dateToAdate(latestDate.minus({ days: 28 })),
            )}
          />
        )}

        {props.label && !props.noLabel && (
          <Typography
            variant="body2"
            sx={{ display: "flex", alignItems: "center", textAlign: "center" }}
          >
            {props.label}
          </Typography>
        )}
        {!props.label && !props.noLabel && (
          <Typography
            variant="body2"
            sx={{ display: "flex", alignItems: "center", textAlign: "center" }}
          >
            From {props.earliestDate} <br />
            To {props.latestDate}
          </Typography>
        )}

        {props.showNav && props.getNavUrl && (
          <NavAfter
            to={props.getNavUrl(
              dateToAdate(earliestDate.plus({ days: 28 })),
              dateToAdate(latestDate.plus({ days: 28 })),
            )}
          />
        )}
      </Stack>

      <OneYear
        earliestDate={props.earliestDate}
        latestDate={props.latestDate}
        currentToday={props.currentToday}
        data={data}
      />
    </StyledDiv>
  );
}

interface NavBeforeProps {
  to: string;
}

function NavBefore(props: NavBeforeProps) {
  return (
    <IconButton
      aria-label="previous-interval"
      size="large"
      component={Link}
      to={props.to}
    >
      <ArrowBackIosNewIcon fontSize="inherit" />
    </IconButton>
  );
}

interface NavAfterProps {
  to: string;
}

function NavAfter(props: NavAfterProps) {
  return (
    <IconButton
      aria-label="next-interval"
      size="large"
      component={Link}
      to={props.to}
    >
      <ArrowForwardIosIcon fontSize="inherit" />
    </IconButton>
  );
}

interface OneYearProps {
  earliestDate: ADate;
  latestDate: ADate;
  currentToday: ADate;
  data: Map<string, number>;
}

function OneYear(props: OneYearProps) {
  const earliestDateAtWeekStart = aDateToDate(props.earliestDate).startOf(
    "week",
  );
  const latestDateAtWeekStart = aDateToDate(props.latestDate);

  const weeksBetween = [];
  let currentDate = earliestDateAtWeekStart;
  while (currentDate < latestDateAtWeekStart) {
    weeksBetween.push(currentDate);
    currentDate = currentDate.plus({ weeks: 1 });
  }

  return (
    <Stack
      direction="row"
      sx={{ marginLeft: "auto", marginRight: "auto", width: "fit-content" }}
    >
      {weeksBetween.map((weekStart, index) => {
        return (
          <OneCol key={index} weekStart={weekStart} currentToday={props.currentToday}>
            {Array.from({ length: 7 }).map((_, dayIndex) => {
              const day = weekStart.plus({ days: dayIndex });
              const value = props.data.get(day.toISODate()!);
              const theValue = value !== undefined ? `- ${value}%` : "";
              const tooltip = `${day.toISODate()} ${theValue}`;
              return (
                <Tooltip key={dayIndex} title={tooltip}>
                  <span>
                    <OneCell doneness={value} />
                  </span>
                </Tooltip>
              );
            })}
          </OneCol>
        );
      })}
    </Stack>
  );
}

interface OneColProps extends PropsWithChildren {
  weekStart: DateTime<true>;
  currentToday: ADate;
}

function OneCol(props: OneColProps) {
  const currentTodayWeek = aDateToDate(props.currentToday).startOf("week");
  const isCurrentWeek = props.weekStart.equals(currentTodayWeek);

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        backgroundColor: isCurrentWeek ? (theme) => theme.palette.info.light : 'transparent',
      }}
    >
      {props.children}
    </Box>
  );
}

interface OneCellProps {
  doneness: number | undefined;
}

function OneCell(props: OneCellProps) {
  return (
    <Box
      sx={{
        width: "1rem",
        height: "1rem",
        margin: "1px",
        backgroundColor: bucketedColorScale(props.doneness),
      }}
    ></Box>
  );
}

function computeDonenessForStreakMark(streakMark: HabitStreakMark): number {
  // look at number of done statuses in streakMark.statuses
  let doneStatuses = 0;
  let allStatuses = 0;
  for (const status of Object.values(streakMark.statuses)) {
    if (status === InboxTaskStatus.DONE) {
      doneStatuses++;
    }
    allStatuses++;
  }
  return Math.floor((doneStatuses / allStatuses) * 100);
}

function bucketedColorScale(value: number | undefined): string {
  if (value === undefined || value === null) return "#eeeeee";
  if (value <= 10) return "#e57373"; // reddish
  if (value <= 50) return "#ffb74d"; // orange-ish
  if (value <= 90) return "#fff176"; // yellow-ish
  return "#81c784"; // green-ish
}

const StyledDiv = styled("div")`
  display: flex;
  justify-content: space-between;
  flex-direction: column;
`;

import {
  ADate,
  Habit,
  HabitStreakMark,
  InboxTaskStatus,
} from "@jupiter/webapi-client";
import {
  Box,
  IconButton,
  Stack,
  Theme,
  Tooltip,
  Typography,
  useTheme,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import { PropsWithChildren } from "react";
import ArrowBackIosNewIcon from "@mui/icons-material/ArrowBackIosNew";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import { Link } from "@remix-run/react";
import { DateTime } from "luxon";

import { aDateToDate, dateToAdate } from "~/logic/domain/adate";

const CELL_SIZE = (theme: Theme) => theme.typography.htmlFontSize - 2;
export const CELL_FULL_SIZE = (theme: Theme) => CELL_SIZE(theme) + 2;

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

  const dataPerDay: Map<string, number> = new Map();
  for (const streakMark of props.streakMarks) {
    dataPerDay.set(
      streakMark.date,
      computeDonenessForStreakMark(streakMark.statuses),
    );
  }

  const dataPerWeek: Map<string, number> = new Map();
  const mergedStatuses: Record<string, Record<string, InboxTaskStatus>> = {};
  for (const streakMark of props.streakMarks) {
    const weekStart = aDateToDate(streakMark.date).startOf("week").toISODate()!;
    if (!mergedStatuses[weekStart]) {
      mergedStatuses[weekStart] = {};
    }
    for (const [key, value] of Object.entries(streakMark.statuses)) {
      mergedStatuses[weekStart][key] = value;
    }
  }
  for (const [weekStart, statuses] of Object.entries(mergedStatuses)) {
    dataPerWeek.set(weekStart, computeDonenessForStreakMark(statuses));
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
        weeksBetween={weeksBetween}
        currentToday={props.currentToday}
        dataPerDay={dataPerDay}
        dataPerWeek={dataPerWeek}
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
  currentToday: ADate;
  weeksBetween: DateTime<true>[];
  dataPerDay: Map<string, number>;
  dataPerWeek: Map<string, number>;
}

function OneYear(props: OneYearProps) {
  const theme = useTheme();
  return (
    <Stack
      direction="row"
      sx={{ marginLeft: "auto", marginRight: "auto", width: "fit-content" }}
    >
      {props.weeksBetween.map((weekStart, index) => {
        const weekTooltip = `Week of ${weekStart.toISODate()}`;
        return (
          <OneCol
            key={index}
            weekStart={weekStart}
            currentToday={props.currentToday}
          >
            <Tooltip title={weekTooltip}>
              <span>
                <OneCell
                  isToday={false}
                  isFuture={false}
                  doneness={props.dataPerWeek.get(weekStart.toISODate()!)}
                />
              </span>
            </Tooltip>

            <span
              style={{
                paddingBottom: "0.5rem",
                background: theme.palette.background.paper,
              }}
            ></span>

            {Array.from({ length: 7 }).map((_, dayIndex) => {
              const day = weekStart.plus({ days: dayIndex });
              const value = props.dataPerDay.get(day.toISODate()!);
              const theValue = value !== undefined ? `- ${value}%` : "";
              const isToday = props.currentToday == day.toISODate();
              const tooltip = isToday
                ? "Today"
                : `${day.toISODate()} ${theValue}`;
              return (
                <Tooltip key={dayIndex} title={tooltip}>
                  <span>
                    <OneCell
                      isToday={isToday}
                      isFuture={day.toISODate() > props.currentToday}
                      doneness={value}
                    />
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
        backgroundColor: isCurrentWeek
          ? (theme) => theme.palette.info.light
          : "transparent",
      }}
    >
      {props.children}
    </Box>
  );
}

interface OneCellProps {
  isToday: boolean;
  isFuture: boolean;
  doneness: number | undefined;
}

function OneCell(props: OneCellProps) {
  const theme = useTheme();
  return (
    <Box
      sx={{
        width: CELL_SIZE(theme),
        height: CELL_SIZE(theme),
        margin: "1px",
        backgroundColor: props.isToday
          ? "#ffd700"
          : props.isFuture
            ? theme.palette.info.light
            : bucketedColorScale(props.doneness),
      }}
    ></Box>
  );
}

function computeDonenessForStreakMark(
  statuses: Record<string, InboxTaskStatus>,
): number {
  // look at number of done statuses in streakMark.statuses
  let doneStatuses = 0;
  let allStatuses = 0;
  for (const status of Object.values(statuses)) {
    if (status === InboxTaskStatus.DONE) {
      doneStatuses++;
    }
    allStatuses++;
  }
  if (allStatuses === 0) {
    return 0;
  }
  return Math.floor((doneStatuses / allStatuses) * 100);
}

function bucketedColorScale(value: number | undefined): string {
  if (value === undefined || value === null) return "#eeeeee";
  if (value <= 15) return "#e57373"; // reddish
  if (value <= 30) return "#ef9a9a"; // lighter red
  if (value <= 45) return "#ffb74d"; // orange
  if (value <= 60) return "#fff176"; // yellow
  if (value <= 75) return "#aed581"; // light green
  return "#81c784"; // green
}

const StyledDiv = styled("div")`
  display: flex;
  justify-content: space-between;
  flex-direction: column;
`;

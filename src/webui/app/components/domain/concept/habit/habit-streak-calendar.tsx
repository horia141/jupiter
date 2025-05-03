import {
  Habit,
  HabitStreakMark,
  InboxTask,
  InboxTaskStatus,
} from "@jupiter/webapi-client";
import ArrowBackIosNewIcon from "@mui/icons-material/ArrowBackIosNew";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import { Box, IconButton, Typography, Stack, Button } from "@mui/material";
import { styled } from "@mui/material/styles";
import { CalendarTooltipProps, ResponsiveTimeRange } from "@nivo/calendar";
import { Link } from "@remix-run/react";

import { aDateToDate } from "~/logic/domain/adate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { EntityNameComponent } from "~/components/infra/entity-name";
import { InboxTaskStatusTag } from "~/components/domain/concept/inbox-task/inbox-task-status-tag";

interface HabitStreakCalendarProps {
  year: number;
  currentYear: number;
  habit: Habit;
  streakMarks: HabitStreakMark[];
  inboxTasks: InboxTask[];
  getYearUrl: (year: number) => string;
}

export function HabitStreakCalendar(props: HabitStreakCalendarProps) {
  const isBigScreen = useBigScreen();
  const earliestDate = aDateToDate(`${props.year}-01-01`);
  const latestDate = aDateToDate(`${props.year}-12-31`);
  const inboxTaskById: Map<string, InboxTask> = new Map(
    props.inboxTasks.map((it) => [it.ref_id, it]),
  );

  const data = props.streakMarks.map((streakMark) => {
    return {
      value: computeDonenessForStreakMark(streakMark),
      day: streakMark.date,
    };
  });

  function handleTooltip(tooltipProps: CalendarTooltipProps) {
    const theStreakMark = props.streakMarks.find(
      (d) => d.date === tooltipProps.day,
    );
    if (!theStreakMark) {
      return null;
    }

    return (
      <TooltipBox
        sx={{
          backgroundColor: "white",
        }}
      >
        <Stack>
          {Object.entries(theStreakMark.statuses).map(([taskId, status]) => {
            const taskIdStr = taskId.toString(); // Sometimes it's a int!
            return (
              <TooltipItem key={taskId}>
                <EntityNameComponent
                  compact
                  name={
                    inboxTaskById.has(taskIdStr)
                      ? inboxTaskById.get(taskIdStr)!.name
                      : `Task ${taskIdStr}`
                  }
                />
                <InboxTaskStatusTag status={status} />
              </TooltipItem>
            );
          })}
        </Stack>
      </TooltipBox>
    );
  }

  function renderCalendar(from: string, to: string) {
    return (
      <Box sx={{ height: "200px" }}>
        <ResponsiveTimeRange
          data={data}
          from={from}
          to={to}
          weekdayLegendOffset={0}
          weekdayTicks={[]}
          minValue={0}
          maxValue={100}
          emptyColor="#eeeeee"
          colorScale={bucketedColorScale}
          tooltip={handleTooltip}
          align="center"
          margin={{
            top: 40,
            right: 0,
            bottom: 0,
            left: 0,
          }}
        />
      </Box>
    );
  }

  return (
    <StyledDiv>
      <Stack
        direction="row"
        sx={{ justifyContent: "center", alignItems: "center", gap: 2 }}
      >
        <IconButton
          component={Link}
          to={props.getYearUrl(props.year - 1)}
          aria-label="previous-year"
          size="large"
        >
          <ArrowBackIosNewIcon fontSize="inherit" />
        </IconButton>
        <Typography sx={{ textAlign: "center" }}>Year {props.year}</Typography>
        <Button component={Link} to={props.getYearUrl(props.currentYear)}>
          Go To Current Year ({props.currentYear})
        </Button>
        <IconButton
          component={Link}
          to={props.getYearUrl(props.year + 1)}
          aria-label="next-year"
          size="large"
          disabled={props.year === props.currentYear}
        >
          <ArrowForwardIosIcon fontSize="inherit" />
        </IconButton>
      </Stack>
      {isBigScreen ? (
        renderCalendar(earliestDate.toISODate(), latestDate.toISODate())
      ) : (
        <Stack spacing={2}>
          {renderCalendar(`${props.year}-01-01`, `${props.year}-03-31`)}
          {renderCalendar(`${props.year}-04-01`, `${props.year}-06-30`)}
          {renderCalendar(`${props.year}-07-01`, `${props.year}-09-30`)}
          {renderCalendar(`${props.year}-10-01`, `${props.year}-12-31`)}
        </Stack>
      )}
    </StyledDiv>
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

const bucketedColorScale = (value: number | { valueOf(): number }) => {
  const num = typeof value === "number" ? value : value.valueOf();
  if (num === undefined || num === null) return "#eeeeee";
  if (num <= 10) return "#e57373"; // reddish
  if (num <= 50) return "#ffb74d"; // orange-ish
  if (num <= 90) return "#fff176"; // yellow-ish
  return "#81c784"; // green-ish
};

bucketedColorScale.ticks = () => {
  return [0, 10, 50, 90, 100];
};

const TooltipBox = styled("div")`
  font-size: 1rem;
  border: 1px dashed gray;
  padding: 5px;
  border-radius: 5px;
  z-index: 1000;
`;

const TooltipItem = styled(Box)`
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 5px;
`;

const StyledDiv = styled("div")`
  display: flex;
  justify-content: space-between;
  flex-direction: column;
`;

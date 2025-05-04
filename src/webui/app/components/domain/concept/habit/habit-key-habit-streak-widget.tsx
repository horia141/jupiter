import { Habit, InboxTask, HabitStreakMark } from "@jupiter/webapi-client";
import { Box, Card, Stack, Tab, Tabs } from "@mui/material";
import { Fragment, useState } from "react";

import { HabitStreakCalendar } from "~/components/domain/concept/habit/habit-streak-calendar";

const ANIMATION_DURATION_MS = 10_000;

interface Entry {
  habit: Habit;
  streakMarks: HabitStreakMark[];
  inboxTasks: InboxTask[];
}

interface HabitKeyHabitStreakWidgetProps {
  year: number;
  currentYear: number;
  entries: Entry[];
  getYearUrl: (year: number) => string;
}

export function HabitKeyHabitStreakWidget(
  props: HabitKeyHabitStreakWidgetProps,
) {
  const [selectedEntry, setSelectedEntry] = useState<number>(0);

  setTimeout(() => {
    setSelectedEntry((entry) => (entry + 1) % props.entries.length);
  }, ANIMATION_DURATION_MS);

  return (
    <Card>
      <Stack>
        <Tabs
          value={selectedEntry}
          onChange={(_, value) => setSelectedEntry(value)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {props.entries.map((entry, index) => (
            <Tab key={index} label={entry.habit.name} />
          ))}
        </Tabs>
        {props.entries.map((entry, index) => (
          <Fragment key={index}>
            {index === selectedEntry && (
              <Box sx={{ margin: "0.4rem" }}>
                <HabitStreakCalendar
                  year={props.year}
                  currentYear={props.currentYear}
                  habit={entry.habit}
                  streakMarks={entry.streakMarks}
                  inboxTasks={entry.inboxTasks}
                  getYearUrl={props.getYearUrl}
                  alwaysWide
                />
              </Box>
            )}
          </Fragment>
        ))}
      </Stack>
    </Card>
  );
}

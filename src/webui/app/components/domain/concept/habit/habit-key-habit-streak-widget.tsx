import { Box, Stack, Tab, Tabs } from "@mui/material";
import { Fragment, useEffect, useState } from "react";

import { HabitStreakCalendar } from "~/components/domain/concept/habit/habit-streak-calendar";
import {
  WidgetContainer,
  WidgetProps,
} from "~/components/domain/application/home/common";
import { DocsHelpSubject } from "~/components/infra/docs-help";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";

const ANIMATION_DURATION_MS = 10_000;

export function HabitKeyHabitStreakWidget(props: WidgetProps) {
  const habitStreak = props.habitStreak!;
  const [selectedEntry, setSelectedEntry] = useState<number>(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setSelectedEntry((entry) => (entry + 1) % habitStreak.entries.length);
    }, ANIMATION_DURATION_MS);
    return () => clearInterval(interval);
  }, [habitStreak.entries]);

  if (habitStreak.entries.length === 0) {
    return (
      <WidgetContainer>
        <EntityNoNothingCard
          title="No Key Habit Streaks"
          message="No key habit streaks found. You can create a new habit to start a streak."
          newEntityLocations="/app/workspace/habits/new"
          helpSubject={DocsHelpSubject.HABITS}
        />
      </WidgetContainer>
    );
  }

  return (
    <WidgetContainer>
      <Stack>
        <Tabs
          value={selectedEntry}
          onChange={(_, value) => setSelectedEntry(value)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {habitStreak.entries.map((entry, index) => (
            <Tab key={index} label={entry.habit.name} />
          ))}
        </Tabs>
        {habitStreak.entries.map((entry, index) => (
          <Fragment key={index}>
            {index === selectedEntry && (
              <Box sx={{ margin: "0.4rem" }}>
                <HabitStreakCalendar
                  year={habitStreak.year}
                  currentYear={habitStreak.currentYear}
                  habit={entry.habit}
                  streakMarks={entry.streakMarks}
                  inboxTasks={entry.inboxTasks}
                  getYearUrl={habitStreak.getYearUrl}
                  alwaysWide
                />
              </Box>
            )}
          </Fragment>
        ))}
      </Stack>
    </WidgetContainer>
  );
}

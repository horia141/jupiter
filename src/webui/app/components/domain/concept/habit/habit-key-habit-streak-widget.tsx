import { Box, Stack, Tab, Tabs } from "@mui/material";
import { Fragment, useEffect, useState } from "react";
import { WidgetDimension } from "@jupiter/webapi-client";

import { HabitStreakCalendar } from "~/components/domain/concept/habit/habit-streak-calendar";
import { WidgetProps } from "~/components/domain/application/home/common";
import { DocsHelpSubject } from "~/components/infra/docs-help";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";
import { limitKeyHabitResultsBasedOnScreenSize } from "~/logic/domain/habit-streak";
import { useBigScreen } from "~/rendering/use-big-screen";

const ANIMATION_DURATION_MS = 10_000;

const DAYS_TO_SHOW_ON_BIG_SCREEN_3x1 = 365;
const DAYS_TO_SHOW_ON_BIG_SCREEN_2x1 = 240;
const DAYS_TO_SHOW_ON_SMALL_SCREEN = 90;

export function HabitKeyHabitStreakWidget(props: WidgetProps) {
  const habitStreak = props.habitStreak!;
  const [selectedEntry, setSelectedEntry] = useState<number>(0);

  const isBigScreen = useBigScreen();

  const habitsByRefId = new Map(
    habitStreak.entries.map((e) => [e.habit.ref_id, e.habit]),
  );

  const keyHabitStreaks = limitKeyHabitResultsBasedOnScreenSize(
    habitStreak.entries.map((e) => ({
      habitRefId: e.habit.ref_id,
      streakMarkEarliestDate: habitStreak.earliestDate,
      streakMarkLatestDate: habitStreak.latestDate,
      streakMarks: e.streakMarks,
    })),
    isBigScreen
      ? props.geometry.dimension === WidgetDimension.DIM_3X1
        ? DAYS_TO_SHOW_ON_BIG_SCREEN_3x1
        : DAYS_TO_SHOW_ON_BIG_SCREEN_2x1
      : DAYS_TO_SHOW_ON_SMALL_SCREEN,
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setSelectedEntry((entry) => (entry + 1) % habitStreak.entries.length);
    }, ANIMATION_DURATION_MS);
    return () => clearInterval(interval);
  }, [habitStreak.entries]);

  if (habitStreak.entries.length === 0) {
    return (
      <EntityNoNothingCard
        title="No Key Habit Streaks"
        message="No key habit streaks found. You can create a new habit to start a streak."
        newEntityLocations="/app/workspace/habits/new"
        helpSubject={DocsHelpSubject.HABITS}
      />
    );
  }

  return (
    <>
      <Stack>
        <Tabs
          value={selectedEntry}
          onChange={(_, value) => setSelectedEntry(value)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {keyHabitStreaks.map((entry, index) => (
            <Tab
              key={index}
              label={
                habitsByRefId.get(entry.habitRefId)?.name ?? "Unknown Habit"
              }
            />
          ))}
        </Tabs>
        {keyHabitStreaks.map((entry, index) => (
          <Fragment key={index}>
            {index === selectedEntry && (
              <Box sx={{ margin: "0.4rem" }}>
                <HabitStreakCalendar
                  earliestDate={entry.streakMarkEarliestDate}
                  latestDate={entry.streakMarkLatestDate}
                  currentToday={habitStreak.currentToday}
                  habit={habitsByRefId.get(entry.habitRefId)!}
                  streakMarks={entry.streakMarks}
                  label={habitStreak.label}
                  showNav={habitStreak.showNav}
                  getNavUrl={habitStreak.getNavUrl}
                />
              </Box>
            )}
          </Fragment>
        ))}
      </Stack>
    </>
  );
}

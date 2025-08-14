import { Box, Stack, Tab, Tabs, Typography, useTheme } from "@mui/material";
import { Fragment, useEffect, useRef, useState } from "react";

import {
  CELL_FULL_SIZE,
  HabitStreakCalendar,
} from "~/components/domain/concept/habit/habit-streak-calendar";
import { WidgetProps } from "~/components/domain/application/home/common";
import { DocsHelpSubject } from "~/components/infra/docs-help";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";
import {
  KeyHabitStreak,
  limitKeyHabitResultsBasedOnScreenSize,
} from "~/logic/domain/habit-streak";
import {
  isWidgetDimensionKSized,
  widgetDimensionCols,
  widgetDimensionRows,
} from "~/logic/widget";

const ANIMATION_DURATION_MS = 10_000;

export function HabitKeyHabitStreakWidget(props: WidgetProps) {
  const habitStreak = props.habitStreak!;
  const theme = useTheme();
  const widgetContainer = useRef<HTMLDivElement>(null);

  const dimensionCols = widgetDimensionCols(props.geometry.dimension);
  const dimensionRows = widgetDimensionRows(props.geometry.dimension);

  const [keyHabitStreaks, setKeyHabitStreaks] = useState<KeyHabitStreak[]>([]);

  useEffect(() => {
    if (!widgetContainer.current) {
      return;
    }

    const containerWidth = widgetContainer.current.clientWidth;
    // Each cell has 1rem in width and 2px borders. Each column is 7 cells,
    // corresponding to a week, so we need to look at the below number of cells.
    const daysToInclude =
      (Math.floor(containerWidth / CELL_FULL_SIZE(theme)) - 1) * 7;

    setKeyHabitStreaks(
      limitKeyHabitResultsBasedOnScreenSize(
        habitStreak.entries.map((e) => ({
          habitRefId: e.habit.ref_id,
          streakMarkEarliestDate: habitStreak.earliestDate,
          streakMarkLatestDate: habitStreak.latestDate,
          streakMarks: e.streakMarks,
        })),
        daysToInclude,
      ),
    );
  }, [
    theme,
    habitStreak.earliestDate,
    habitStreak.entries,
    habitStreak.latestDate,
    theme.typography.htmlFontSize,
  ]);

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
    <Box id="habit-key-habit-streak-widget-container" ref={widgetContainer}>
      {!isWidgetDimensionKSized(props.geometry.dimension) &&
      dimensionRows === 1 &&
      dimensionCols >= 1 ? (
        <HorizontalStreak
          widgetProps={props}
          keyHabitStreak={keyHabitStreaks}
        />
      ) : (
        <VerticalStreak widgetProps={props} keyHabitStreak={keyHabitStreaks} />
      )}
    </Box>
  );
}

interface HorizontalStreakProps {
  widgetProps: WidgetProps;
  keyHabitStreak: KeyHabitStreak[];
}

function HorizontalStreak({
  widgetProps,
  keyHabitStreak,
}: HorizontalStreakProps) {
  const [selectedEntry, setSelectedEntry] = useState<number>(0);
  const habitStreak = widgetProps.habitStreak!;
  const habitsByRefId = new Map(
    habitStreak.entries.map((e) => [e.habit.ref_id, e.habit]),
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setSelectedEntry((entry) => (entry + 1) % habitStreak.entries.length);
    }, ANIMATION_DURATION_MS);
    return () => clearInterval(interval);
  }, [habitStreak.entries]);

  return (
    <>
      <Stack>
        <Tabs
          value={selectedEntry}
          onChange={(_, value) => setSelectedEntry(value)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ marginBottom: "0.5rem" }}
        >
          {keyHabitStreak.map((entry, index) => (
            <Tab
              key={index}
              label={
                habitsByRefId.get(entry.habitRefId)?.name ?? "Unknown Habit"
              }
            />
          ))}
        </Tabs>
        {keyHabitStreak.map((entry, index) => (
          <Fragment key={index}>
            {index === selectedEntry && (
              <HabitStreakCalendar
                earliestDate={entry.streakMarkEarliestDate}
                latestDate={entry.streakMarkLatestDate}
                currentToday={habitStreak.currentToday}
                habit={habitsByRefId.get(entry.habitRefId)!}
                streakMarks={entry.streakMarks}
                noLabel={habitStreak.noLabel}
                label={habitStreak.label}
                showNav={habitStreak.showNav}
                getNavUrl={habitStreak.getNavUrl}
              />
            )}
          </Fragment>
        ))}
      </Stack>
    </>
  );
}

interface VerticalStreakProps {
  widgetProps: WidgetProps;
  keyHabitStreak: KeyHabitStreak[];
}

function VerticalStreak({ widgetProps, keyHabitStreak }: VerticalStreakProps) {
  const habitStreak = widgetProps.habitStreak!;
  const habitsByRefId = new Map(
    habitStreak.entries.map((e) => [e.habit.ref_id, e.habit]),
  );

  return (
    <Stack spacing={2}>
      {keyHabitStreak.map((entry, index) => (
        <Fragment key={index}>
          <Typography variant="h6" noWrap>
            {habitsByRefId.get(entry.habitRefId)?.name ?? "Unknown Habit"}
          </Typography>
          <HabitStreakCalendar
            earliestDate={entry.streakMarkEarliestDate}
            latestDate={entry.streakMarkLatestDate}
            currentToday={habitStreak.currentToday}
            habit={habitsByRefId.get(entry.habitRefId)!}
            streakMarks={entry.streakMarks}
            noLabel={habitStreak.noLabel}
            label={habitStreak.label}
            showNav={habitStreak.showNav}
            getNavUrl={habitStreak.getNavUrl}
          />
        </Fragment>
      ))}
    </Stack>
  );
}

import type {
  ADate,
  HabitFindResultEntry,
  HabitLoadResult,
  Project,
} from "@jupiter/webapi-client";
import { WidgetDimension, WorkspaceFeature } from "@jupiter/webapi-client";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { useContext } from "react";
import { DateTime } from "luxon";
import { z } from "zod";
import { parseQuery } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { TopLevelInfoContext } from "~/top-level-context";
import { basicShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DifficultyTag } from "~/components/domain/core/difficulty-tag";
import { DocsHelpSubject } from "~/components/infra/docs-help";
import { EisenTag } from "~/components/domain/core/eisen-tag";
import { EntityNameComponent } from "~/components/infra/entity-name";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { PeriodTag } from "~/components/domain/core/period-tag";
import { ProjectTag } from "~/components/domain/concept/project/project-tag";
import { sortHabitsNaturally } from "~/logic/domain/habit";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { IsKeyTag } from "~/components/domain/core/is-key-tag";
import { HabitKeyHabitStreakWidget } from "~/components/domain/concept/habit/habit-key-habit-streak-widget";
import { WidgetProps } from "~/components/domain/application/home/common";

export const handle = {
  displayType: DisplayType.TRUNK,
};

const QuerySchema = z.object({
  includeStreakMarksEarliestDate: z.string().optional(),
  includeStreakMarksLatestDate: z.string().optional(),
});

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const query = parseQuery(request, QuerySchema);

  const response = await apiClient.habits.habitFind({
    allow_archived: false,
    include_notes: false,
    include_project: true,
    include_inbox_tasks: false,
  });

  let earliestDate = query.includeStreakMarksEarliestDate;
  let latestDate = query.includeStreakMarksLatestDate;
  if (earliestDate === undefined) {
    earliestDate = DateTime.now().minus({ days: 365 }).toISODate();
    latestDate = DateTime.now().toISODate();
  }

  const keyHabitRefIds = response.entries
    .filter((e) => e.habit.is_key)
    .map((e) => e.habit.ref_id);

  let keyHabitResults: HabitLoadResult[] = [];
  if (keyHabitRefIds.length > 0) {
    keyHabitResults = await Promise.all(
      keyHabitRefIds.map((refId) =>
        apiClient.habits.habitLoad({
          ref_id: refId,
          allow_archived: false,
          include_streak_marks_earliest_date: earliestDate,
          include_streak_marks_latest_date: latestDate,
        }),
      ),
    );
  }

  return json({
    habits: response.entries,
    keyHabitStreaks: keyHabitResults.map((h) => ({
      habitRefId: h.habit.ref_id,
      streakMarkEarliestDate: h.streak_mark_earliest_date,
      streakMarkLatestDate: h.streak_mark_latest_date,
      streakMarks: h.streak_marks,
    })),
  });
}

export const shouldRevalidate: ShouldRevalidateFunction = basicShouldRevalidate;

export default function Habits() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedHabits = sortHabitsNaturally(
    loaderData.habits.map((e) => e.habit),
  );
  const entriesByRefId = new Map<string, HabitFindResultEntry>();
  for (const entry of loaderData.habits) {
    entriesByRefId.set(entry.habit.ref_id, entry);
  }

  const rightNow = DateTime.local({ zone: topLevelInfo.user.timezone });

  const widgetProps: WidgetProps = {
    rightNow,
    timezone: topLevelInfo.user.timezone,
    topLevelInfo,
    habitStreak: {
      earliestDate:
        loaderData.keyHabitStreaks[0]?.streakMarkEarliestDate ??
        topLevelInfo.today,
      latestDate:
        loaderData.keyHabitStreaks[0]?.streakMarkLatestDate ??
        topLevelInfo.today,
      currentToday: topLevelInfo.today,
      entries: loaderData.keyHabitStreaks.map((h) => ({
        habit: entriesByRefId.get(h.habitRefId)!.habit,
        streakMarks: h.streakMarks,
      })),
      showNav: true,
      getNavUrl: (earliestDate: ADate, latestDate: ADate) => {
        return `/app/workspace/habits?includeStreakMarksEarliestDate=${earliestDate}&includeStreakMarksLatestDate=${latestDate}`;
      },
    },
    geometry: {
      row: 0,
      col: 0,
      dimension: WidgetDimension.DIM_3X1,
    },
  };

  return (
    <TrunkPanel
      key={"habits"}
      createLocation="/app/workspace/habits/new"
      returnLocation="/app/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        {sortedHabits.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no habits to show. You can create a new habit."
            newEntityLocations="/app/workspace/habits/new"
            helpSubject={DocsHelpSubject.HABITS}
          />
        )}

        {loaderData.keyHabitStreaks.length > 0 && (
          <HabitKeyHabitStreakWidget {...widgetProps} />
        )}

        <EntityStack>
          {sortedHabits.map((habit) => {
            const entry = entriesByRefId.get(
              habit.ref_id,
            ) as HabitFindResultEntry;
            return (
              <EntityCard
                key={`habit-${habit.ref_id}`}
                entityId={`habit-${habit.ref_id}`}
              >
                <EntityLink to={`/app/workspace/habits/${habit.ref_id}`}>
                  <IsKeyTag isKey={habit.is_key} />
                  <EntityNameComponent name={habit.name} />
                  {isWorkspaceFeatureAvailable(
                    topLevelInfo.workspace,
                    WorkspaceFeature.PROJECTS,
                  ) && <ProjectTag project={entry.project as Project} />}
                  {habit.suspended && <span className="tag">Suspended</span>}
                  <PeriodTag period={habit.gen_params.period} />
                  {habit.gen_params.eisen && (
                    <EisenTag eisen={habit.gen_params.eisen} />
                  )}
                  {habit.gen_params.difficulty && (
                    <DifficultyTag difficulty={habit.gen_params.difficulty} />
                  )}
                </EntityLink>
              </EntityCard>
            );
          })}
        </EntityStack>
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary("/app/workspace", {
  error: () => `There was an error loading the habits! Please try again!`,
});

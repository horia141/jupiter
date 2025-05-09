import type {
  HabitFindResultEntry,
  HabitLoadResult,
  Project,
} from "@jupiter/webapi-client";
import { WorkspaceFeature } from "@jupiter/webapi-client";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet, useSearchParams } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { useContext } from "react";
import { z } from "zod";
import { parseQuery } from "zodix";
import { DateTime } from "luxon";

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
import { newURLParams } from "~/logic/domain/navigation";

export const handle = {
  displayType: DisplayType.TRUNK,
};

const QuerySchema = z.object({
  includeStreakMarksForYear: z
    .string()
    .transform((s) => parseInt(s, 10))
    .optional(),
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
          include_streak_marks_for_year: query.includeStreakMarksForYear,
        }),
      ),
    );
  }

  return json({
    habits: response.entries,
    keyHabitResults: keyHabitResults.map((h) => ({
      habit: h.habit,
      streakMarkYear: h.streak_mark_year,
      streakMarks: h.streak_marks,
      inboxTasks: h.inbox_tasks,
    })),
  });
}

export const shouldRevalidate: ShouldRevalidateFunction = basicShouldRevalidate;

export default function Habits() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const [query] = useSearchParams();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedHabits = sortHabitsNaturally(
    loaderData.habits.map((e) => e.habit),
  );
  const entriesByRefId = new Map<string, HabitFindResultEntry>();
  for (const entry of loaderData.habits) {
    entriesByRefId.set(entry.habit.ref_id, entry);
  }

  const rightNow = DateTime.now();

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

        {loaderData.keyHabitResults.length > 0 && (
          <HabitKeyHabitStreakWidget
            year={
              loaderData.keyHabitResults[0]?.streakMarkYear ?? rightNow.year
            }
            currentYear={rightNow.year}
            entries={loaderData.keyHabitResults}
            getYearUrl={(year) =>
              `/app/workspace/habits?${newURLParams(
                query,
                "includeStreakMarksForYear",
                year.toString(),
              )}`
            }
          />
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

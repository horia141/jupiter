import type { HabitFindResultEntry, Project } from "@jupiter/webapi-client";
import { WorkspaceFeature } from "@jupiter/webapi-client";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { useContext } from "react";

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

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.habits.habitFind({
    allow_archived: false,
    include_notes: false,
    include_project: true,
    include_inbox_tasks: false,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction = basicShouldRevalidate;

export default function Habits() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedHabits = sortHabitsNaturally(entries.map((e) => e.habit));
  const entriesByRefId = new Map<string, HabitFindResultEntry>();
  for (const entry of entries) {
    entriesByRefId.set(entry.habit.ref_id, entry);
  }

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

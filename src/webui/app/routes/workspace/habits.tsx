import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { Outlet, ShouldRevalidateFunction, useFetcher } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import type { Habit, HabitFindResultEntry, Project } from "jupiter-gen";
import { Eisen, RecurringTaskPeriod, WorkspaceFeature } from "jupiter-gen";
import { useContext } from "react";
import { getLoggedInApiClient } from "~/api-clients";
import { DifficultyTag } from "~/components/difficulty-tag";
import { EisenTag } from "~/components/eisen-tag";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { PeriodTag } from "~/components/period-tag";
import { ProjectTag } from "~/components/project-tag";
import { sortHabitsNaturally } from "~/logic/domain/habit";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const response = await getLoggedInApiClient(session).habit.findHabit({
    allow_archived: false,
    include_project: true,
    include_inbox_tasks: false,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Habits() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedHabits = sortHabitsNaturally(entries.map((e) => e.habit));
  const entriesByRefId = new Map<string, HabitFindResultEntry>();
  for (const entry of entries) {
    entriesByRefId.set(entry.habit.ref_id.the_id, entry);
  }

  const archiveHabitFetch = useFetcher();

  function archiveHabit(habit: Habit) {
    archiveHabitFetch.submit(
      {
        intent: "archive",
        name: "NOT USED - FOR ARCHIVE ONLY",
        project: "NOT USED - FOR ARCHIVE ONLY",
        period: RecurringTaskPeriod.DAILY,
        eisen: Eisen.REGULAR,
      },
      {
        method: "post",
        action: `/workspace/habits/${habit.ref_id.the_id}`,
      }
    );
  }

  return (
    <TrunkPanel
      createLocation="/workspace/habits/new"
      returnLocation="/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
          {sortedHabits.map((habit) => {
            const entry = entriesByRefId.get(
              habit.ref_id.the_id
            ) as HabitFindResultEntry;
            return (
              <EntityCard
                key={habit.ref_id.the_id}
                allowSwipe
                allowMarkNotDone
                onMarkNotDone={() => archiveHabit(habit)}
              >
                <EntityLink to={`/workspace/habits/${habit.ref_id.the_id}`}>
                  <EntityNameComponent name={habit.name} />
                  {isWorkspaceFeatureAvailable(
                    topLevelInfo.workspace,
                    WorkspaceFeature.PROJECTS
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

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the habits! Please try again!`
);

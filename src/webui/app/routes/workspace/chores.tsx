import type { ChoreFindResultEntry, Project } from "@jupiter/webapi-client";
import { WorkspaceFeature } from "@jupiter/webapi-client";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { useContext } from "react";
import { getLoggedInApiClient } from "~/api-clients.server";
import Check from "~/components/check";
import { DifficultyTag } from "~/components/difficulty-tag";
import { EisenTag } from "~/components/eisen-tag";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { PeriodTag } from "~/components/period-tag";
import { ProjectTag } from "~/components/project-tag";
import { sortChoresNaturally } from "~/logic/domain/chore";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.chores.choreFind({
    allow_archived: false,
    include_project: true,
    include_inbox_tasks: false,
    include_notes: false,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Chores() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedChores = sortChoresNaturally(entries.map((e) => e.chore));
  const entriesByRefId = new Map<string, ChoreFindResultEntry>();
  for (const entry of entries) {
    entriesByRefId.set(entry.chore.ref_id, entry);
  }

  return (
    <TrunkPanel
      key={"chores"}
      createLocation="/workspace/chores/new"
      returnLocation="/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
          {sortedChores.map((chore) => {
            const entry = entriesByRefId.get(
              chore.ref_id
            ) as ChoreFindResultEntry;
            return (
              <EntityCard
                key={`chore-${chore.ref_id}`}
                entityId={`chore-${chore.ref_id}`}
              >
                <EntityLink to={`/workspace/chores/${chore.ref_id}`}>
                  <EntityNameComponent name={chore.name} />
                  {isWorkspaceFeatureAvailable(
                    topLevelInfo.workspace,
                    WorkspaceFeature.PROJECTS
                  ) && <ProjectTag project={entry.project as Project} />}
                  <Check isDone={!chore.suspended} label="Active" />
                  <PeriodTag period={chore.gen_params.period} />
                  {chore.gen_params.eisen && (
                    <EisenTag eisen={chore.gen_params.eisen} />
                  )}
                  {chore.gen_params.difficulty && (
                    <DifficultyTag difficulty={chore.gen_params.difficulty} />
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

export const ErrorBoundary = makeTrunkErrorBoundary(
  "/workspace",
  () => `There was an error loading the chores! Please try again!`
);

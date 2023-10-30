import { Button } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import {
  Link,
  Outlet,
  ShouldRevalidateFunction,
  useFetcher,
} from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import type { Chore, ChoreFindResultEntry, Project } from "jupiter-gen";
import { Eisen, RecurringTaskPeriod, WorkspaceFeature } from "jupiter-gen";
import { useContext } from "react";
import { getLoggedInApiClient } from "~/api-clients";
import Check from "~/components/check";
import { DifficultyTag } from "~/components/difficulty-tag";
import { EisenTag } from "~/components/eisen-tag";
import { EntityNameComponent } from "~/components/entity-name";
import { ActionHeader } from "~/components/infra/actions-header";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
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
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const response = await getLoggedInApiClient(session).chore.findChore({
    allow_archived: false,
    include_project: true,
    include_inbox_tasks: false,
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
    entriesByRefId.set(entry.chore.ref_id.the_id, entry);
  }

  const archiveChoreFetch = useFetcher();

  function archiveChore(chore: Chore) {
    archiveChoreFetch.submit(
      {
        intent: "archive",
        name: "NOT USED - FOR ARCHIVE ONLY",
        project: "NOT USED - FOR ARCHIVE ONLY",
        period: RecurringTaskPeriod.DAILY,
        eisen: Eisen.REGULAR,
      },
      {
        method: "post",
        action: `/workspace/chores/${chore.ref_id.the_id}`,
      }
    );
  }

  return (
    <TrunkPanel>
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <ActionHeader returnLocation="/workspace">
          <Button
            variant="contained"
            to="/workspace/chores/new"
            component={Link}
          >
            Create
          </Button>
        </ActionHeader>

        <EntityStack>
          {sortedChores.map((chore) => {
            const entry = entriesByRefId.get(
              chore.ref_id.the_id
            ) as ChoreFindResultEntry;
            return (
              <EntityCard
                key={chore.ref_id.the_id}
                allowSwipe
                allowMarkNotDone
                onMarkNotDone={() => archiveChore(chore)}
              >
                <EntityLink to={`/workspace/chores/${chore.ref_id.the_id}`}>
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

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the chores! Please try again!`
);

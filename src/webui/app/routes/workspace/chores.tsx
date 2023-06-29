import { Button } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { Link, useFetcher, useOutlet } from "@remix-run/react";
import type { Chore, ChoreFindResultEntry, Project } from "jupiter-gen";
import { Eisen, RecurringTaskPeriod } from "jupiter-gen";
import { getLoggedInApiClient } from "~/api-clients";
import Check from "~/components/check";
import { DifficultyTag } from "~/components/difficulty-tag";
import { EisenTag } from "~/components/eisen-tag";
import { EntityNameComponent } from "~/components/entity-name";
import { ActionHeader } from "~/components/infra/actions-header";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { LeafPanel } from "~/components/infra/leaf-panel";
import { NestingAwarePanel } from "~/components/infra/nesting-aware-panel";
import { TrunkCard } from "~/components/infra/trunk-card";
import { PeriodTag } from "~/components/period-tag";
import { ProjectTag } from "~/components/project-tag";
import { sortChoresNaturally } from "~/logic/domain/chore";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

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

export default function Chores() {
  const outlet = useOutlet();
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

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
    <TrunkCard>
      <NestingAwarePanel showOutlet={shouldShowALeaf}>
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
                  <ProjectTag project={entry.project as Project} />
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
      </NestingAwarePanel>

      <LeafPanel show={shouldShowALeaf}>{outlet}</LeafPanel>
    </TrunkCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the chores! Please try again!`
);

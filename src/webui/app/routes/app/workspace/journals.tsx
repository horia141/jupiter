import type { JournalFindResultEntry } from "@jupiter/webapi-client";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { useContext } from "react";

import { getLoggedInApiClient } from "~/api-clients.server";
import { DocsHelpSubject } from "~/components/docs-help";
import { EntityNoNothingCard } from "~/components/entity-no-nothing-card";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { JournalStack } from "~/components/journal-stack";
import { sortJournalsNaturally } from "~/logic/domain/journal";
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

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.journals.journalFind({
    allow_archived: false,
    include_notes: false,
    include_writing_tasks: false,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Journals() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedJournals = sortJournalsNaturally(entries.map((e) => e.journal));
  const entriesByRefId = new Map<string, JournalFindResultEntry>();
  for (const entry of entries) {
    entriesByRefId.set(entry.journal.ref_id, entry);
  }

  return (
    <TrunkPanel
      key={"journals"}
      createLocation="/app/workspace/journals/new"
      returnLocation="/app/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        {sortedJournals.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no journals to show. You can create a new journal."
            newEntityLocations="/app/workspace/journals/new"
            helpSubject={DocsHelpSubject.JOURNALS}
          />
        )}

        <JournalStack topLevelInfo={topLevelInfo} journals={sortedJournals} />
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary("/app/workspace", {
  error: () => `There was an error loading the journals! Please try again!`,
});

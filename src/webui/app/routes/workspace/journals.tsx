import type { Journal, JournalFindResultEntry } from "@jupiter/webapi-client";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet, useFetcher } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { useContext } from "react";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
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
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const response = await getLoggedInApiClient(session).journals.journalFind({
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

  const archiveJournalFetch = useFetcher();

  function archiveJournal(journal: Journal) {
    archiveJournalFetch.submit(
      {
        intent: "archive",
      },
      {
        method: "post",
        action: `/workspace/journals/${journal.ref_id}`,
      }
    );
  }

  return (
    <TrunkPanel
      createLocation="/workspace/journals/new"
      returnLocation="/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <JournalStack
          topLevelInfo={topLevelInfo}
          journals={sortedJournals}
          allowSwipe
          allowMarkNotDone
          onMarkNotDone={(journal) => archiveJournal(journal)}
        />
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the journals! Please try again!`
);

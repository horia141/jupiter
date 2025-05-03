import type {
  JournalFindResultEntry,
  JournalStats,
} from "@jupiter/webapi-client";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { useContext } from "react";
import TuneIcon from "@mui/icons-material/Tune";

import { getLoggedInApiClient } from "~/api-clients.server";
import { DocsHelpSubject } from "~/components/infra/docs-help";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { JournalStack } from "~/components/domain/concept/journal/journal-stack";
import { sortJournalsNaturally } from "~/logic/domain/journal";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowBranch,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";
import { SectionActions, NavSingle } from "~/components/infra/section-actions";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.journals.journalFind({
    allow_archived: false,
    include_notes: false,
    include_writing_tasks: false,
    include_journal_stats: true,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Journals() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowABranch = useTrunkNeedsToShowBranch();
  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedJournals = sortJournalsNaturally(entries.map((e) => e.journal));
  const entriesByRefId = new Map<string, JournalFindResultEntry>();
  for (const entry of entries) {
    entriesByRefId.set(entry.journal.ref_id, entry);
  }
  const journalStatsByJournalRefId = new Map<string, JournalStats>();
  for (const entry of entries) {
    journalStatsByJournalRefId.set(entry.journal.ref_id, entry.journal_stats!);
  }

  return (
    <TrunkPanel
      key={"journals"}
      createLocation="/app/workspace/journals/new"
      returnLocation="/app/workspace"
      actions={
        <SectionActions
          id="journals"
          topLevelInfo={topLevelInfo}
          inputsEnabled={true}
          actions={[
            NavSingle({
              text: "Settings",
              link: `/app/workspace/journals/settings`,
              icon: <TuneIcon />,
            }),
          ]}
        />
      }
    >
      <NestingAwareBlock
        branchForceHide={shouldShowABranch}
        shouldHide={shouldShowABranch || shouldShowALeaf}
      >
        {sortedJournals.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no journals to show. You can create a new journal."
            newEntityLocations="/app/workspace/journals/new"
            helpSubject={DocsHelpSubject.JOURNALS}
          />
        )}

        <JournalStack
          topLevelInfo={topLevelInfo}
          journals={sortedJournals}
          journalStatsByJournalRefId={journalStatsByJournalRefId}
        />
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

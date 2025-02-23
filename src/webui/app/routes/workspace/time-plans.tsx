import type { TimePlanFindResultEntry } from "@jupiter/webapi-client";
import type { LoaderArgs } from "@remix-run/node";
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
import { TimePlanStack } from "~/components/time-plan-stack";
import { sortTimePlansNaturally } from "~/logic/domain/time-plan";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowBranch,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.timePlans.timePlanFind({
    allow_archived: false,
    include_notes: false,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function TimePlans() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowABranch = useTrunkNeedsToShowBranch();
  const shouldShowALeafToo = useTrunkNeedsToShowLeaf();

  const sortedTimePlans = sortTimePlansNaturally(
    entries.map((e) => e.time_plan)
  );
  const entriesByRefId = new Map<string, TimePlanFindResultEntry>();
  for (const entry of entries) {
    entriesByRefId.set(entry.time_plan.ref_id, entry);
  }

  return (
    <TrunkPanel
      key={"time-plans"}
      createLocation="/workspace/time-plans/new"
      returnLocation="/workspace"
    >
      <NestingAwareBlock
        branchForceHide={shouldShowABranch}
        shouldHide={shouldShowABranch || shouldShowALeafToo}
      >
        {sortedTimePlans.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no time plans to show. You can create a new time plan."
            newEntityLocations="/workspace/time-plans/new"
            helpSubject={DocsHelpSubject.TIME_PLANS}
          />
        )}

        <TimePlanStack
          topLevelInfo={topLevelInfo}
          timePlans={sortedTimePlans}
        />
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary(
  "/workspace",
  () => `There was an error loading the time plans! Please try again!`
);

import type { TimePlan, TimePlanFindResultEntry } from "@jupiter/webapi-client";
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
import { TimePlanStack } from "~/components/time-plan-stack";
import { sortTimePlansNaturally } from "~/logic/domain/time-plan";
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
  const response = await getLoggedInApiClient(session).timePlans.timePlanFind({
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

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedTimePlans = sortTimePlansNaturally(
    entries.map((e) => e.time_plan)
  );
  const entriesByRefId = new Map<string, TimePlanFindResultEntry>();
  for (const entry of entries) {
    entriesByRefId.set(entry.time_plan.ref_id, entry);
  }

  const archiveTimePlanFetch = useFetcher();

  function archiveTimePlan(timePlan: TimePlan) {
    archiveTimePlanFetch.submit(
      {
        intent: "archive",
      },
      {
        method: "post",
        action: `/workspace/time-plans/${timePlan.ref_id}`,
      }
    );
  }

  return (
    <TrunkPanel
    key={"time-plans"}
      createLocation="/workspace/time-plans/new"
      returnLocation="/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <TimePlanStack
          topLevelInfo={topLevelInfo}
          timePlans={sortedTimePlans}
          allowSwipe
          allowMarkNotDone
          onMarkNotDone={(timePlan) => archiveTimePlan(timePlan)}
        />
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the time plans! Please try again!`
);

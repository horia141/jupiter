import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet, useFetcher } from "@remix-run/react";

import {
  type WorkingMem,
  type WorkingMemFindResultEntry,
} from "@jupiter/webapi-client";

import { AnimatePresence } from "framer-motion";
import { DateTime } from "luxon";
import { getLoggedInApiClient } from "~/api-clients.server";
import { ADateTag } from "~/components/adate-tag";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { PeriodTag } from "~/components/period-tag";
import { aDateToDate } from "~/logic/domain/adate";
import { sortWorkingMemsNaturally } from "~/logic/domain/working-mem";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.workingMem.workingMemFind({
    allow_archived: false,
    include_notes: false,
    include_cleanup_tasks: false,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function WorkingMemArchive({ request }: LoaderArgs) {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const sortedWorkingMems = sortWorkingMemsNaturally(
    entries.map((e) => e.working_mem)
  );
  const workingMemsByRefId = new Map<string, WorkingMemFindResultEntry>();
  for (const entry of entries) {
    workingMemsByRefId.set(entry.working_mem.ref_id, entry);
  }

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const archiveWorkingMemFetch = useFetcher();

  function archiveWorkingMem(workingmem: WorkingMem) {
    archiveWorkingMemFetch.submit(
      {
        intent: "archive",
      },
      {
        method: "post",
        action: `/workspace/working-mem/archive/${workingmem.ref_id}`,
      }
    );
  }

  const today = DateTime.now();

  return (
    <BranchPanel
      key={`working-mem/archive}`}
      returnLocation="/workspace/working-mem"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
          {sortedWorkingMems.map((workingMem) => {
            return (
              <EntityCard
                entityId={`working-mem-${workingMem.ref_id}`}
                key={`working-mem-${workingMem.ref_id}`}
                allowSwipe
                allowMarkNotDone={
                  aDateToDate(workingMem.right_now) > today.minus({ days: 14 })
                }
                onMarkNotDone={() => archiveWorkingMem(workingMem)}
              >
                <EntityLink
                  to={`/workspace/working-mem/archive/${workingMem.ref_id}`}
                >
                  <EntityNameComponent name={workingMem.name} />
                  <ADateTag label="Date" date={workingMem.right_now} />
                  <PeriodTag period={workingMem.period} />
                </EntityLink>
              </EntityCard>
            );
          })}
        </EntityStack>
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </BranchPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the vacations! Please try again!`
);

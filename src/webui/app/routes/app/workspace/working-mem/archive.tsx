import { type WorkingMemFindResultEntry } from "@jupiter/webapi-client";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";

import { getLoggedInApiClient } from "~/api-clients.server";
import { ADateTag } from "~/components/adate-tag";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeBranchErrorBoundary } from "~/components/infra/error-boundary";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { PeriodTag } from "~/components/period-tag";
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

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.workingMem.workingMemFind({
    allow_archived: true,
    include_notes: false,
    include_cleanup_tasks: false,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function WorkingMemArchive() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const sortedWorkingMems = sortWorkingMemsNaturally(
    entries.map((e) => e.working_mem),
  );
  const workingMemsByRefId = new Map<string, WorkingMemFindResultEntry>();
  for (const entry of entries) {
    workingMemsByRefId.set(entry.working_mem.ref_id, entry);
  }

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  return (
    <BranchPanel
      key={`working-mem/archive}`}
      returnLocation="/app/workspace/working-mem"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
          {sortedWorkingMems.map((workingMem) => {
            return (
              <EntityCard
                entityId={`working-mem-${workingMem.ref_id}`}
                key={`working-mem-${workingMem.ref_id}`}
              >
                <EntityLink
                  to={`/app/workspace/working-mem/archive/${workingMem.ref_id}`}
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

export const ErrorBoundary = makeBranchErrorBoundary(
  "/app/workspace/working-mem",
  {
    error: () => `There was an error loading the vacations! Please try again!`,
  },
);

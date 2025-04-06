import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";

import { getLoggedInApiClient } from "~/api-clients.server";
import { DocsHelpSubject } from "~/components/docs-help";
import EntityIconComponent from "~/components/entity-icon";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityNoNothingCard } from "~/components/entity-no-nothing-card";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowBranch,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const smartListResponse = await apiClient.smartLists.smartListFind({
    allow_archived: false,
    include_notes: false,
    include_tags: false,
    include_items: false,
    include_item_notes: false,
  });

  return json({
    entries: smartListResponse.entries,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function SmartLists() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();

  const shouldShowABranch = useTrunkNeedsToShowBranch();
  const shouldShowALeafToo = useTrunkNeedsToShowLeaf();

  return (
    <TrunkPanel
      key={"smart-lists"}
      createLocation="/app/workspace/smart-lists/new"
      returnLocation="/app/workspace"
    >
      <NestingAwareBlock
        branchForceHide={shouldShowABranch}
        shouldHide={shouldShowABranch || shouldShowALeafToo}
      >
        <EntityStack>
          {loaderData.entries.length === 0 && (
            <EntityNoNothingCard
              title="You Have To Start Somewhere"
              message="There are no smart lists to show. You can create a new smart list."
              newEntityLocations="/app/workspace/smart-lists/new"
              helpSubject={DocsHelpSubject.SMART_LISTS}
            />
          )}
          {loaderData.entries.map((entry) => (
            <EntityCard
              key={`smart-list-${entry.smart_list.ref_id}`}
              entityId={`smart-list-${entry.smart_list.ref_id}`}
            >
              <EntityLink
                to={`/app/workspace/smart-lists/${entry.smart_list.ref_id}/items`}
              >
                {entry.smart_list.icon && (
                  <EntityIconComponent icon={entry.smart_list.icon} />
                )}
                <EntityNameComponent name={entry.smart_list.name} />
              </EntityLink>
            </EntityCard>
          ))}
        </EntityStack>
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary("/app/workspace", {
  error: () => `There was an error loading the smart lists! Please try again!`,
});

import type { SmartList } from "@jupiter/webapi-client";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet, useFetcher } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { getLoggedInApiClient } from "~/api-clients";
import EntityIconComponent from "~/components/entity-icon";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowBranch,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const smartListResponse = await getLoggedInApiClient(
    session
  ).smartLists.smartListFind({
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

  const archiveSmarListFetch = useFetcher();

  function archiveSmartList(smartList: SmartList) {
    archiveSmarListFetch.submit(
      {
        intent: "archive",
        name: "NOT USED - FOR ARCHIVE ONLY",
      },
      {
        method: "post",
        action: `/workspace/smart-lists/${smartList.ref_id}/items/details`,
      }
    );
  }

  return (
    <TrunkPanel
      createLocation="/workspace/smart-lists/new"
      returnLocation="/workspace"
    >
      <NestingAwareBlock
        branchForceHide={shouldShowABranch}
        shouldHide={shouldShowABranch || shouldShowALeafToo}
      >
        <EntityStack>
          {loaderData.entries.map((entry) => (
            <EntityCard
              key={entry.smart_list.ref_id}
              allowSwipe
              allowMarkNotDone
              onMarkNotDone={() => archiveSmartList(entry.smart_list)}
            >
              <EntityLink
                to={`/workspace/smart-lists/${entry.smart_list.ref_id}/items`}
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

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the smart lists! Please try again!`
);

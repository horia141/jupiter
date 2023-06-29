import { Button, ButtonGroup } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { Link, useFetcher, useOutlet } from "@remix-run/react";
import type { SmartList } from "jupiter-gen";
import { getLoggedInApiClient } from "~/api-clients";
import EntityIconComponent from "~/components/entity-icon";
import { EntityNameComponent } from "~/components/entity-name";
import { ActionHeader } from "~/components/infra/actions-header";
import { BranchPanel } from "~/components/infra/branch-panel";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { LeafPanel } from "~/components/infra/leaf-panel";
import { NestingAwarePanel } from "~/components/infra/nesting-aware-panel";
import { TrunkCard } from "~/components/infra/trunk-card";
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
  ).smartList.findSmartList({
    allow_archived: false,
    include_tags: false,
    include_items: false,
  });

  return json({
    entries: smartListResponse.entries,
  });
}

export default function SmartLists() {
  const outlet = useOutlet();
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
        action: `/workspace/smart-lists/${smartList.ref_id.the_id}/items/details`,
      }
    );
  }

  return (
    <TrunkCard>
      <NestingAwarePanel
        branchForceHide={shouldShowABranch}
        showOutlet={shouldShowABranch || shouldShowALeafToo}
      >
        <ActionHeader returnLocation="/workspace">
          <ButtonGroup>
            <Button
              variant="contained"
              to={`/workspace/smart-lists/new`}
              component={Link}
            >
              Create
            </Button>
          </ButtonGroup>
        </ActionHeader>

        <EntityStack>
          {loaderData.entries.map((entry) => (
            <EntityCard
              key={entry.smart_list.ref_id.the_id}
              allowSwipe
              allowMarkNotDone
              onMarkNotDone={() => archiveSmartList(entry.smart_list)}
            >
              <EntityLink
                to={`/workspace/smart-lists/${entry.smart_list.ref_id.the_id}/items`}
              >
                {entry.smart_list.icon && (
                  <EntityIconComponent icon={entry.smart_list.icon} />
                )}
                <EntityNameComponent name={entry.smart_list.name} />
              </EntityLink>
            </EntityCard>
          ))}
        </EntityStack>
      </NestingAwarePanel>

      <BranchPanel show={shouldShowABranch}>{outlet}</BranchPanel>

      <LeafPanel show={!shouldShowABranch && shouldShowALeafToo}>
        {outlet}
      </LeafPanel>
    </TrunkCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the smart lists! Please try again!`
);

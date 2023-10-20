import { Button, ButtonGroup } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import {
  Link,
  ShouldRevalidateFunction,
  useFetcher,
  useOutlet,
} from "@remix-run/react";
import { WorkspaceFeature, type Metric } from "jupiter-gen";
import { useContext } from "react";
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
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowBranch,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const metricResponse = await getLoggedInApiClient(session).metric.findMetric({
    allow_archived: false,
    include_entries: false,
    include_collection_inbox_tasks: false,
  });

  return json({
    entries: metricResponse.entries,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Metrics() {
  const outlet = useOutlet();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowABranch = useTrunkNeedsToShowBranch();
  const shouldShowALeafToo = useTrunkNeedsToShowLeaf();

  const archiveMetricFetch = useFetcher();

  function archiveMetric(smartList: Metric) {
    archiveMetricFetch.submit(
      {
        intent: "archive",
        name: "NOT USED - FOR ARCHIVE ONLY",
      },
      {
        method: "post",
        action: `/workspace/metric/${smartList.ref_id.the_id}/details`,
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
              to={`/workspace/metrics/new`}
              component={Link}
            >
              Create
            </Button>
            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS
            ) && (
              <Button
                variant="outlined"
                to={`/workspace/metrics/settings`}
                component={Link}
              >
                Settings
              </Button>
            )}
          </ButtonGroup>
        </ActionHeader>

        <EntityStack>
          {loaderData.entries.map((entry) => (
            <EntityCard
              key={entry.metric.ref_id.the_id}
              allowSwipe
              allowMarkNotDone
              onMarkNotDone={() => archiveMetric(entry.metric)}
            >
              <EntityLink
                to={`/workspace/metrics/${entry.metric.ref_id.the_id}`}
              >
                {entry.metric.icon && (
                  <EntityIconComponent icon={entry.metric.icon} />
                )}
                <EntityNameComponent name={entry.metric.name} />
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
  () => `There was an error loading the metrics! Please try again!`
);

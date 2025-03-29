import { WorkspaceFeature } from "@jupiter/webapi-client";
import TuneIcon from "@mui/icons-material/Tune";
import { Button, IconButton } from "@mui/material";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { useContext } from "react";
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
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
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

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const metricResponse = await apiClient.metrics.metricFind({
    allow_archived: false,
    include_notes: false,
    include_entries: false,
    include_collection_inbox_tasks: false,
    include_metric_entry_notes: false,
  });

  return json({
    entries: metricResponse.entries,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Metrics() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowABranch = useTrunkNeedsToShowBranch();
  const shouldShowALeafToo = useTrunkNeedsToShowLeaf();

  const isBigScreen = useBigScreen();

  return (
    <TrunkPanel
      key={"metrics"}
      createLocation="/app/workspace/metrics/new"
      extraControls={[
        <>
          {isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.PROJECTS,
          ) && (
            <>
              {isBigScreen ? (
                <Button
                  variant="outlined"
                  to={`/app/workspace/metrics/settings`}
                  component={Link}
                  startIcon={<TuneIcon />}
                >
                  Settings
                </Button>
              ) : (
                <IconButton
                  to={`/app/workspace/metrics/settings`}
                  component={Link}
                >
                  <TuneIcon />
                </IconButton>
              )}
            </>
          )}
        </>,
      ]}
      returnLocation="/app/workspace"
    >
      <NestingAwareBlock
        branchForceHide={shouldShowABranch}
        shouldHide={shouldShowABranch || shouldShowALeafToo}
      >
        {loaderData.entries.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no metrics to show. You can create a new metric."
            newEntityLocations="/app/workspace/metrics/new"
            helpSubject={DocsHelpSubject.METRICS}
          />
        )}
        <EntityStack>
          {loaderData.entries.map((entry) => (
            <EntityCard key={entry.metric.ref_id}>
              <EntityLink to={`/app/workspace/metrics/${entry.metric.ref_id}`}>
                {entry.metric.icon && (
                  <EntityIconComponent icon={entry.metric.icon} />
                )}
                <EntityNameComponent name={entry.metric.name} />
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
  error: () => `There was an error loading the metrics! Please try again!`,
});

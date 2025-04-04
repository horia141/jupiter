import type { MetricEntry } from "@jupiter/webapi-client";
import { ApiError } from "@jupiter/webapi-client";
import TuneIcon from "@mui/icons-material/Tune";
import { Button, IconButton, styled } from "@mui/material";
import { ResponsiveLine } from "@nivo/line";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, Outlet, useNavigation, useParams } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { DocsHelpSubject } from "~/components/docs-help";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityNoNothingCard } from "~/components/entity-no-nothing-card";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeBranchErrorBoundary } from "~/components/infra/error-boundary";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TimeDiffTag } from "~/components/time-diff-tag";
import { aDateToDate, compareADate } from "~/logic/domain/adate";
import { metricEntryName } from "~/logic/domain/metric-entry";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useBranchNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("archive"),
  }),
  z.object({
    intent: z.literal("remove"),
  }),
]);

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  try {
    const response = await apiClient.metrics.metricLoad({
      ref_id: id,
      allow_archived: true,
      allow_archived_entries: false,
    });

    return json({
      metric: response.metric,
      metricEntries: response.metric_entries,
    });
  } catch (error) {
    if (error instanceof ApiError && error.status === StatusCodes.NOT_FOUND) {
      throw new Response(ReasonPhrases.NOT_FOUND, {
        status: StatusCodes.NOT_FOUND,
        statusText: ReasonPhrases.NOT_FOUND,
      });
    }

    throw error;
  }
}

export async function action({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  switch (form.intent) {
    case "archive": {
      await apiClient.metrics.metricArchive({
        ref_id: id,
      });

      return redirect(`/app/workspace/metrics`);
    }

    case "remove": {
      await apiClient.metrics.metricRemove({
        ref_id: id,
      });

      return redirect(`/app/workspace/metrics`);
    }
  }
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Metric() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const shouldShowALeaf = useBranchNeedsToShowLeaf();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const navigation = useNavigation();
  const inputsEnabled = navigation.state === "idle";

  const sortedEntries = [...loaderData.metricEntries].sort((e1, e2) => {
    return -compareADate(e1.collection_time, e2.collection_time);
  });

  const today = DateTime.local({ zone: topLevelInfo.user.timezone });

  const isBigScreen = useBigScreen();

  return (
    <BranchPanel
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.metric.archived}
      key={`metric-${loaderData.metric.ref_id}`}
      createLocation={`/app/workspace/metrics/${loaderData.metric.ref_id}/entries/new`}
      extraControls={[
        isBigScreen ? (
          <Button
            key={loaderData.metric.ref_id}
            variant="outlined"
            to={`/app/workspace/metrics/${loaderData.metric.ref_id}/details`}
            component={Link}
            startIcon={<TuneIcon />}
          >
            Details
          </Button>
        ) : (
          <IconButton
            key={loaderData.metric.ref_id}
            to={`/app/workspace/metrics/${loaderData.metric.ref_id}/details`}
            component={Link}
          >
            <TuneIcon />
          </IconButton>
        ),
      ]}
      returnLocation="/app/workspace/metrics"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <MetricGraph sortedMetricEntries={sortedEntries} />

        {sortedEntries.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no metric entries to show. You can create a new metric entry."
            newEntityLocations={`/app/workspace/metrics/${loaderData.metric.ref_id}/entries/new`}
            helpSubject={DocsHelpSubject.METRICS}
          />
        )}

        <EntityStack>
          {sortedEntries.map((entry) => (
            <EntityCard
              entityId={`metric-entry-${entry.ref_id}`}
              key={`metric-entry-${entry.ref_id}`}
            >
              <EntityLink
                to={`/app/workspace/metrics/${loaderData.metric.ref_id}/entries/${entry.ref_id}`}
              >
                <EntityNameComponent name={metricEntryName(entry)} />
                <TimeDiffTag
                  today={today}
                  labelPrefix="Collected"
                  collectionTime={entry.collection_time}
                />
              </EntityLink>
            </EntityCard>
          ))}
        </EntityStack>
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </BranchPanel>
  );
}

export const ErrorBoundary = makeBranchErrorBoundary("/app/workspace/metrics", {
  notFound: () => `Could not find metric #${useParams().id}!`,
  error: () =>
    `There was an error loading metric #${useParams().id}! Please try again!`,
});

interface MetricGraphProps {
  sortedMetricEntries: MetricEntry[];
}

function MetricGraph({ sortedMetricEntries }: MetricGraphProps) {
  const entriesForGraph = sortedMetricEntries.map((e) => ({
    x: aDateToDate(e.collection_time).toFormat("yyyy-MM-dd"),
    y: e.value,
    refId: e.ref_id,
  }));
  const graphMaxValue = Math.max(...entriesForGraph.map((e) => e.y)) * 1.35;

  return (
    <MetricGraphDiv>
      <ResponsiveLine
        curve="monotoneX"
        xScale={{
          type: "time",
          format: "%Y-%m-%d",
          useUTC: false,
          precision: "day",
        }}
        xFormat="time:%Y-%m-%d"
        yScale={{
          type: "linear",
          nice: true,
          min: 0,
          max: graphMaxValue,
        }}
        axisBottom={{
          format: "%y-%b",
          tickValues: 7,
        }}
        pointSize={4}
        pointBorderWidth={1}
        pointBorderColor={{
          from: "color",
          modifiers: [["darker", 0.3]],
        }}
        margin={{ top: 20, right: 10, bottom: 50, left: 50 }}
        useMesh={true}
        enableSlices={false}
        data={[
          {
            id: "metricValue",
            data: entriesForGraph,
          },
        ]}
      />
    </MetricGraphDiv>
  );
}

const MetricGraphDiv = styled("div")`
  height: 300px;
`;

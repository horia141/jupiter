import { ResponsiveLine } from "@nivo/line";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import {
  Link,
  Outlet,
  ShouldRevalidateFunction,
  useFetcher,
  useParams,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import type { MetricEntry } from "jupiter-gen";
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { parseParams } from "zodix";

import TuneIcon from "@mui/icons-material/Tune";
import { Button, styled } from "@mui/material";
import { AnimatePresence } from "framer-motion";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNameComponent } from "~/components/entity-name";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TimeDiffTag } from "~/components/time-diff-tag";
import { aDateToDate, compareADate } from "~/logic/domain/adate";
import { metricEntryName } from "~/logic/domain/metric-entry";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useBranchNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const ParamsSchema = {
  id: z.string(),
};

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);

  try {
    const response = await getLoggedInApiClient(session).metrics.metricLoad({
      ref_id: id,
      allow_archived: false,
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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Metric() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const shouldShowALeaf = useBranchNeedsToShowLeaf();

  const sortedEntries = [...loaderData.metricEntries].sort((e1, e2) => {
    return -compareADate(e1.collection_time, e2.collection_time);
  });

  const archiveTagFetch = useFetcher();

  function archiveEntry(item: MetricEntry) {
    archiveTagFetch.submit(
      {
        intent: "archive",
        collectionTime: "NOT USED - FOR ARCHIVE ONLY",
        value: "0",
      },
      {
        method: "post",
        action: `/workspace/metrics/${loaderData.metric.ref_id}/entries/${item.ref_id}`,
      }
    );
  }

  return (
    <BranchPanel
      key={loaderData.metric.ref_id}
      createLocation={`/workspace/metrics/${loaderData.metric.ref_id}/entries/new`}
      extraControls={[
        <Button
          variant="outlined"
          to={`/workspace/metrics/${loaderData.metric.ref_id}/details`}
          component={Link}
          startIcon={<TuneIcon />}
        >
          Details
        </Button>,
      ]}
      returnLocation="/workspace/metrics"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <MetricGraph sortedMetricEntries={sortedEntries} />

        <EntityStack>
          {sortedEntries.map((entry) => (
            <EntityCard
              key={entry.ref_id}
              allowSwipe
              allowMarkNotDone
              onMarkNotDone={() => archiveEntry(entry)}
            >
              <EntityLink
                to={`/workspace/metrics/${loaderData.metric.ref_id}/entries/${entry.ref_id}`}
              >
                <EntityNameComponent name={metricEntryName(entry)} />
                <TimeDiffTag
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

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find metric #${useParams().key}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading metric #${useParams().key}! Please try again!`
);

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

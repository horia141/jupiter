import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Divider,
  styled,
} from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useTransition } from "@remix-run/react";
import { getLoggedInApiClient } from "~/api-clients";
import { EntitySummaryLink } from "~/components/entity-summary-link";
import { EventSourceTag } from "~/components/event-source-tag";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { TimeDiffTag } from "~/components/time-diff-tag";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const summaryResponse = await getLoggedInApiClient(
    session
  ).getSummaries.getSummaries({
    include_schedule_streams: true,
  });
  const response = await getLoggedInApiClient(
    session
  ).schedule.scheduleExternalSyncLoadRuns({});

  return json({
    scheduleStreams: summaryResponse.schedule_streams!,
    entries: response.entries,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function CalendarSettings() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();

  const scheduleStreamsByRefId = new Map(
    loaderData.scheduleStreams.map((stream) => [stream.ref_id, stream])
  );

  return (
    <BranchPanel key="calendar-settings" returnLocation="/workspace/calendar">
      {loaderData.entries.map((entry) => {
        return (
          <Accordion key={entry.ref_id}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <AccordionHeader>
                Run from <EventSourceTag source={entry.source} />
                with {entry.entity_records.length}
                {entry.even_more_entity_records ? "+" : ""} entities synced
                <TimeDiffTag
                  labelPrefix="from"
                  collectionTime={entry.created_time}
                />
              </AccordionHeader>
            </AccordionSummary>

            <AccordionDetails>
              <ExternalSyncTargetsSection>
                Synced Streams
                {entry.per_stream_results.map((stream) => (
                  <EntityCard key={stream.schedule_stream_ref_id}>
                    <EntityLink
                      to={`/workspace/calendar/schedule/stream/${stream.schedule_stream_ref_id}`}
                    >
                      {scheduleStreamsByRefId.get(stream.schedule_stream_ref_id)
                        ?.name || "Archived Stream"}
                    </EntityLink>

                    {stream.error_msg && (
                      <Box>
                        <ErrorDisplay>{stream.error_msg}</ErrorDisplay>
                      </Box>
                    )}
                  </EntityCard>
                ))}
              </ExternalSyncTargetsSection>

              {entry.entity_records.length > 0 && (
                <>
                  <Divider>Entities</Divider>

                  {entry.entity_records.map((record) => (
                    <EntityCard key={record.ref_id}>
                      <EntitySummaryLink summary={record} />
                    </EntityCard>
                  ))}
                </>
              )}
            </AccordionDetails>
          </Accordion>
        );
      })}
    </BranchPanel>
  );
}

const AccordionHeader = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  gap: theme.spacing(1),
  flexWrap: "wrap",
}));

const ErrorDisplay = styled("pre")(({ theme }) => ({
  color: theme.palette.error.main,
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
}));

const ExternalSyncTargetsSection = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  gap: theme.spacing(1),
  flexWrap: "wrap",
  paddingBottom: theme.spacing(1),
}));

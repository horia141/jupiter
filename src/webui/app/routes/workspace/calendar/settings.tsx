import { ApiError, EventSource, ScheduleSource } from "@jupiter/webapi-client";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  Divider,
  FormControl,
  FormControlLabel,
  InputLabel,
  styled,
  Switch,
  Typography,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Form, useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { CheckboxAsString, parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntitySummaryLink } from "~/components/entity-summary-link";
import { EventSourceTag } from "~/components/event-source-tag";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { FieldError } from "~/components/infra/errors";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { ScheduleStreamMultiSelect } from "~/components/schedule-stream-multi-select";
import { TimeDiffTag } from "~/components/time-diff-tag";
import {
  noErrorNoData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { selectZod } from "~/logic/select";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const ScheduleExternalSyncFormSchema = {
  scheduleStreamRefIds: selectZod(z.string()),
  syncEvenIfNotModified: CheckboxAsString,
};

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

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, ScheduleExternalSyncFormSchema);

  try {
    await getLoggedInApiClient(session).schedule.scheduleExternalSyncDo({
      source: EventSource.WEB,
      sync_even_if_not_modified: form.syncEvenIfNotModified,
      filter_schedule_stream_ref_id: form.scheduleStreamRefIds,
    });

    return json(noErrorNoData());
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status === StatusCodes.UNPROCESSABLE_ENTITY
    ) {
      return json(validationErrorToUIErrorInfo(error.body));
    }

    throw error;
  }
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function CalendarSettings() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  const scheduleStreamsByRefId = new Map(
    loaderData.scheduleStreams.map((stream) => [stream.ref_id, stream])
  );

  return (
    <BranchPanel key="calendar-settings" returnLocation="/workspace/calendar">
      <Form method="post">
        <Card>
          <CardContent>
            <FormControl fullWidth>
              <InputLabel id="scheduleStreamRefId">Schedule Streams</InputLabel>
              <ScheduleStreamMultiSelect
                labelId="scheduleStreamRefIds"
                label="Schedule Streams"
                name="scheduleStreamRefIds"
                readOnly={!inputsEnabled}
                allScheduleStreams={loaderData.scheduleStreams.filter(
                  (ss) => ss.source === ScheduleSource.EXTERNAL_ICAL
                )}
              />
              <FieldError
                actionResult={actionData}
                fieldName="/filter_schedule_stream_ref_id"
              />

              <FormControl fullWidth>
                <FormControlLabel
                  control={
                    <Switch
                      name="syncEvenIfNotModified"
                      readOnly={!inputsEnabled}
                      disabled={!inputsEnabled}
                      defaultChecked={false}
                    />
                  }
                  label="Sync Even If Not Modified"
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/sync_even_if_not_modified"
                />
              </FormControl>
            </FormControl>
          </CardContent>

          <CardActions>
            <ButtonGroup>
              <Button
                variant="contained"
                disabled={!inputsEnabled}
                type="submit"
                name="intent"
                value="sync"
              >
                Sync
              </Button>
            </ButtonGroup>
          </CardActions>
        </Card>
      </Form>

      <Divider style={{ paddingTop: "1rem", paddingBottom: "1rem" }}>
        <Typography variant="h6">Previous Runs</Typography>
      </Divider>

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
                  <EntityCard
                    key={`calendar-streams-${entry.ref_id}-${stream.schedule_stream_ref_id}`}
                  >
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
                    <EntityCard
                      key={`entities-${entry.ref_id}-${record.ref_id}`}
                    >
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

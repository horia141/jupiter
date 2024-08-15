import type { ScheduleStreamSummary } from "@jupiter/webapi-client";
import { ApiError, NoteDomain } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  FormControl,
  InputLabel,
  OutlinedInput,
  Stack,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  useActionData,
  useParams,
  useSearchParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionMultipleSpread,
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { ScheduleStreamSelect } from "~/components/schedule-stream-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { basicShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
    startDate: z.string(),
    durationDays: z.string().transform((v) => parseInt(v, 10)),
  }),
  z.object({
    intent: z.literal("change-schedule-stream"),
    scheduleStreamRefId: z.string(),
  }),
  z.object({
    intent: z.literal("create-note"),
  }),
  z.object({
    intent: z.literal("archive"),
  }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);

  const summaryResponse = await getLoggedInApiClient(
    session
  ).getSummaries.getSummaries({
    include_schedule_streams: true,
  });

  try {
    const response = await getLoggedInApiClient(
      session
    ).eventFullDays.scheduleEventFullDaysLoad({
      ref_id: id,
      allow_archived: true,
    });

    return json({
      allScheduleStreams:
        summaryResponse.schedule_streams as Array<ScheduleStreamSummary>,
      scheduleEventFullDays: response.schedule_event_full_days,
      timeEventFullDaysBlock: response.time_event_full_days_block,
      note: response.note,
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

export async function action({ request, params }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);
  const url = new URL(request.url);

  try {
    switch (form.intent) {
      case "update": {
        await getLoggedInApiClient(
          session
        ).eventFullDays.scheduleEventFullDaysUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
          start_date: {
            should_change: true,
            value: form.startDate,
          },
          duration_days: {
            should_change: true,
            value: form.durationDays,
          },
        });
        return redirect(
          `/workspace/calendar/schedule/event-full-days/${id}?${url.searchParams}`
        );
      }
      case "change-schedule-stream": {
        await getLoggedInApiClient(
          session
        ).eventFullDays.scheduleEventFullDaysChangeScheduleStream({
          ref_id: id,
          schedule_stream_ref_id: form.scheduleStreamRefId,
        });
        return redirect(
          `/workspace/calendar/schedule/event-full-days/${id}?${url.searchParams}`
        );
      }
      case "create-note": {
        await getLoggedInApiClient(session).notes.noteCreate({
          domain: NoteDomain.SCHEDULE_EVENT_FULL_DAYS,
          source_entity_ref_id: id,
          content: [],
        });
        return redirect(
          `/workspace/calendar/schedule/event-full-days/${id}?${url.searchParams}`
        );
      }
      case "archive": {
        await getLoggedInApiClient(
          session
        ).eventFullDays.scheduleEventFullDaysArchive({
          ref_id: id,
        });
        return redirect(
          `/workspace/calendar/schedule/event-full-days/${id}?${url.searchParams}`
        );
      }

      default:
        throw new Response("Bad Intent", { status: 500 });
    }
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

export const shouldRevalidate: ShouldRevalidateFunction = basicShouldRevalidate;

export default function ScheduleEventFullDaysViewOne() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const transition = useTransition();
  const [query] = useSearchParams();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.scheduleEventFullDays.archived;

  const [durationDays, setDurationDays] = useState(
    loaderData.timeEventFullDaysBlock.duration_days
  );
  useEffect(() => {
    setDurationDays(loaderData.timeEventFullDaysBlock.duration_days);
  }, [loaderData.timeEventFullDaysBlock.duration_days]);

  const allScheduleStreamsByRefId = new Map(
    loaderData.allScheduleStreams.map((st) => [st.ref_id, st])
  );

  return (
    <LeafPanel
      key={`schedule-event-full-days-${loaderData.scheduleEventFullDays.ref_id}`}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation={`/workspace/calendar?${query}`}
    >
      <GlobalError actionResult={actionData} />
      <SectionCardNew
        id="schedule-event-full-days-properties"
        title="Properties"
        actions={
          <SectionActions
            id="schedule-event-full-days-properties"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionMultipleSpread({
                actions: [
                  ActionSingle({
                    text: "Save",
                    value: "update",
                    highlight: true,
                  }),
                  ActionSingle({
                    text: "Change Stream",
                    value: "change-schedule-stream",
                  }),
                ],
              }),
            ]}
          />
        }
      >
        <Stack spacing={2} useFlexGap>
          <FormControl fullWidth>
            <InputLabel id="scheduleStreamRefId">Schedule Stream</InputLabel>
            <ScheduleStreamSelect
              labelId="scheduleStreamRefId"
              label="Schedule Stream"
              name="scheduleStreamRefId"
              readOnly={!inputsEnabled}
              allScheduleStreams={loaderData.allScheduleStreams}
              defaultValue={
                allScheduleStreamsByRefId.get(
                  loaderData.scheduleEventFullDays.schedule_stream_ref_id
                )!
              }
            />
            <FieldError
              actionResult={actionData}
              fieldName="/schedule_stream_ref_id"
            />
          </FormControl>
          <FormControl fullWidth>
            <InputLabel id="name">Name</InputLabel>
            <OutlinedInput
              label="name"
              name="name"
              readOnly={!inputsEnabled}
              defaultValue={loaderData.scheduleEventFullDays.name}
            />
            <FieldError actionResult={actionData} fieldName="/name" />
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="startDate" shrink margin="dense">
              Start Date
            </InputLabel>
            <OutlinedInput
              type="date"
              label="startDate"
              name="startDate"
              readOnly={!inputsEnabled}
              defaultValue={loaderData.timeEventFullDaysBlock.start_date}
            />

            <FieldError actionResult={actionData} fieldName="/start_date" />
          </FormControl>

          <Stack spacing={2} direction="row">
            <ButtonGroup variant="outlined">
              <Button
                disabled={!inputsEnabled}
                variant={durationDays === 1 ? "contained" : "outlined"}
                onClick={() => setDurationDays(1)}
              >
                1D
              </Button>
              <Button
                disabled={!inputsEnabled}
                variant={durationDays === 3 ? "contained" : "outlined"}
                onClick={() => setDurationDays(3)}
              >
                3d
              </Button>
              <Button
                disabled={!inputsEnabled}
                variant={durationDays === 7 ? "contained" : "outlined"}
                onClick={() => setDurationDays(7)}
              >
                7d
              </Button>
            </ButtonGroup>

            <FormControl fullWidth>
              <InputLabel id="durationDays" shrink margin="dense">
                Duration (Days)
              </InputLabel>
              <OutlinedInput
                type="number"
                label="Duration (Days)"
                name="durationDays"
                readOnly={!inputsEnabled}
                value={durationDays}
                onChange={(e) => setDurationDays(parseInt(e.target.value, 10))}
              />

              <FieldError
                actionResult={actionData}
                fieldName="/duration_days"
              />
            </FormControl>
          </Stack>
        </Stack>
      </SectionCardNew>

      <Card>
        {!loaderData.note && (
          <CardActions>
            <ButtonGroup>
              <Button
                variant="contained"
                disabled={!inputsEnabled}
                type="submit"
                name="intent"
                value="create-note"
              >
                Create Note
              </Button>
            </ButtonGroup>
          </CardActions>
        )}

        {loaderData.note && (
          <>
            <EntityNoteEditor
              initialNote={loaderData.note}
              inputsEnabled={inputsEnabled}
            />
          </>
        )}
      </Card>
    </LeafPanel>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find schedule event in day#${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading schedule event in day #${
      useParams().id
    }. Please try again!`
);

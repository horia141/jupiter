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
    startTimeInDay: z.string().optional(),
    durationMins: z.string().transform((v) => parseInt(v, 10)),
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
    ).eventInDay.scheduleEventInDayLoad({
      ref_id: id,
      allow_archived: true,
    });

    return json({
      allScheduleStreams:
        summaryResponse.schedule_streams as Array<ScheduleStreamSummary>,
      scheduleEventInDay: response.schedule_event_in_day,
      timeEventInDayBlock: response.time_event_in_day_block,
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
        await getLoggedInApiClient(session).eventInDay.scheduleEventInDayUpdate(
          {
            ref_id: id,
            name: {
              should_change: true,
              value: form.name,
            },
            start_date: {
              should_change: true,
              value: form.startDate,
            },
            start_time_in_day: {
              should_change: true,
              value: form.startTimeInDay,
            },
            duration_mins: {
              should_change: true,
              value: form.durationMins,
            },
          }
        );
        return redirect(
          `/workspace/calendar/schedule/event-in-day/${id}?${url.searchParams}`
        );
      }
      case "change-schedule-stream": {
        await getLoggedInApiClient(
          session
        ).eventInDay.scheduleEventInDayChangeScheduleStream({
          ref_id: id,
          schedule_stream_ref_id: form.scheduleStreamRefId,
        });
        return redirect(
          `/workspace/calendar/schedule/event-in-day/${id}?${url.searchParams}`
        );
      }
      case "create-note": {
        await getLoggedInApiClient(session).notes.noteCreate({
          domain: NoteDomain.SCHEDULE_EVENT_IN_DAY,
          source_entity_ref_id: id,
          content: [],
        });
        return redirect(
          `/workspace/calendar/schedule/event-in-day/${id}?${url.searchParams}`
        );
      }
      case "archive": {
        await getLoggedInApiClient(
          session
        ).eventInDay.scheduleEventInDayArchive({
          ref_id: id,
        });
        return redirect(
          `/workspace/calendar/schedule/event-in-day/${id}?${url.searchParams}`
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

export default function ScheduleEventInDayViewOne() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const transition = useTransition();
  const [query] = useSearchParams();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.scheduleEventInDay.archived;

  const [durationMins, setDurationMins] = useState(
    loaderData.timeEventInDayBlock.duration_mins
  );
  useEffect(() => {
    setDurationMins(loaderData.timeEventInDayBlock.duration_mins);
  }, [loaderData.timeEventInDayBlock.duration_mins]);

  const allScheduleStreamsByRefId = new Map(
    loaderData.allScheduleStreams.map((st) => [st.ref_id, st])
  );

  return (
    <LeafPanel
      key={`schedule-event-in-day-${loaderData.scheduleEventInDay.ref_id}`}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation={`/workspace/calendar?${query}`}
    >
      <GlobalError actionResult={actionData} />
      <SectionCardNew
        id="schedule-event-in-day-properties"
        title="Properties"
        actions={
          <SectionActions
            id="schedule-event-in-day-properties"
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
                  loaderData.scheduleEventInDay.schedule_stream_ref_id
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
              defaultValue={loaderData.scheduleEventInDay.name}
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
              defaultValue={loaderData.timeEventInDayBlock.start_date}
            />

            <FieldError actionResult={actionData} fieldName="/start_date" />
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="startTimeInDay" shrink margin="dense">
              Start Time
            </InputLabel>
            <OutlinedInput
              type="time"
              label="startTimeInDay"
              name="startTimeInDay"
              readOnly={!inputsEnabled}
              defaultValue={loaderData.timeEventInDayBlock.start_time_in_day}
            />

            <FieldError
              actionResult={actionData}
              fieldName="/start_time_in_day"
            />
          </FormControl>

          <Stack spacing={2} direction="row">
            <ButtonGroup variant="outlined">
              <Button
                disabled={!inputsEnabled}
                variant={durationMins === 15 ? "contained" : "outlined"}
                onClick={() => setDurationMins(15)}
              >
                15m
              </Button>
              <Button
                disabled={!inputsEnabled}
                variant={durationMins === 30 ? "contained" : "outlined"}
                onClick={() => setDurationMins(30)}
              >
                30m
              </Button>
              <Button
                disabled={!inputsEnabled}
                variant={durationMins === 60 ? "contained" : "outlined"}
                onClick={() => setDurationMins(60)}
              >
                60m
              </Button>
            </ButtonGroup>

            <FormControl fullWidth>
              <InputLabel id="durationMins" shrink margin="dense">
                Duration (Mins)
              </InputLabel>
              <OutlinedInput
                type="number"
                label="Duration (Mins)"
                name="durationMins"
                readOnly={!inputsEnabled}
                value={durationMins}
                onChange={(e) => setDurationMins(parseInt(e.target.value, 10))}
              />

              <FieldError
                actionResult={actionData}
                fieldName="/duration_mins"
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

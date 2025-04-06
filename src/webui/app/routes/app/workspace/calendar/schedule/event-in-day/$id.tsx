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
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  useActionData,
  useNavigation,
  useSearchParams,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionMultipleSpread,
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { ScheduleStreamSelect } from "~/components/schedule-stream-select";
import { TimeEventParamsSource } from "~/components/time-event-params-source";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { isCorePropertyEditable } from "~/logic/domain/schedule-event-in-day";
import {
  timeEventInDayBlockParamsToTimezone,
  timeEventInDayBlockParamsToUtc,
} from "~/logic/domain/time-event";
import { basicShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({
  id: z.string(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    userTimezone: z.string(),
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
  z.object({
    intent: z.literal("remove"),
  }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_schedule_streams: true,
  });

  try {
    const response = await apiClient.eventInDay.scheduleEventInDayLoad({
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

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);
  const url = new URL(request.url);

  try {
    switch (form.intent) {
      case "update": {
        const { startDate, startTimeInDay } = timeEventInDayBlockParamsToUtc(
          form,
          form.userTimezone,
        );
        await apiClient.eventInDay.scheduleEventInDayUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
          start_date: {
            should_change: true,
            value: startDate,
          },
          start_time_in_day: {
            should_change: true,
            value: startTimeInDay ?? "",
          },
          duration_mins: {
            should_change: true,
            value: form.durationMins,
          },
        });
        return redirect(`/app/workspace/calendar?${url.searchParams}`);
      }

      case "change-schedule-stream": {
        await apiClient.eventInDay.scheduleEventInDayChangeScheduleStream({
          ref_id: id,
          schedule_stream_ref_id: form.scheduleStreamRefId,
        });
        return redirect(
          `/app/workspace/calendar/schedule/event-in-day/${id}?${url.searchParams}`,
        );
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.SCHEDULE_EVENT_IN_DAY,
          source_entity_ref_id: id,
          content: [],
        });
        return redirect(
          `/app/workspace/calendar/schedule/event-in-day/${id}?${url.searchParams}`,
        );
      }

      case "archive": {
        await apiClient.eventInDay.scheduleEventInDayArchive({
          ref_id: id,
        });
        return redirect(`/app/workspace/calendar?${url.searchParams}`);
      }

      case "remove": {
        await apiClient.eventInDay.scheduleEventInDayRemove({
          ref_id: id,
        });
        return redirect(`/app/workspace/calendar?${url.searchParams}`);
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
  const navigation = useNavigation();
  const [query] = useSearchParams();

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.scheduleEventInDay.archived;
  const corePropertyEditable = isCorePropertyEditable(
    loaderData.scheduleEventInDay,
  );

  const blockParamsInTz = timeEventInDayBlockParamsToTimezone(
    {
      startDate: loaderData.timeEventInDayBlock.start_date,
      startTimeInDay: loaderData.timeEventInDayBlock.start_time_in_day,
    },
    topLevelInfo.user.timezone,
  );
  const [startDate, setStartDate] = useState(blockParamsInTz.startDate);
  const [startTimeInDay, setStartTimeInDay] = useState(
    blockParamsInTz.startTimeInDay!,
  );
  const [durationMins, setDurationMins] = useState(
    loaderData.timeEventInDayBlock.duration_mins,
  );

  useEffect(() => {
    const blockParamsInTz = timeEventInDayBlockParamsToTimezone(
      {
        startDate: loaderData.timeEventInDayBlock.start_date,
        startTimeInDay: loaderData.timeEventInDayBlock.start_time_in_day,
      },
      topLevelInfo.user.timezone,
    );
    setStartDate(blockParamsInTz.startDate);
    setStartTimeInDay(blockParamsInTz.startTimeInDay!);
    setDurationMins(loaderData.timeEventInDayBlock.duration_mins);
  }, [loaderData.timeEventInDayBlock, topLevelInfo.user.timezone]);

  const [debounceForeign, setDeoubceForeign] = useState(false);
  setTimeout(() => setDeoubceForeign(true), 100);
  useEffect(() => {
    if (!debounceForeign) {
      return;
    }
    if (query.get("sourceStartDate") && query.get("sourceStartTimeInDay")) {
      setStartDate(query.get("sourceStartDate")!);
      setStartTimeInDay(query.get("sourceStartTimeInDay")!);
    }
    if (query.get("sourceDurationMins")) {
      setDurationMins(parseInt(query.get("sourceDurationMins")!, 10));
    }
  }, [query, debounceForeign]);

  const allScheduleStreamsByRefId = new Map(
    loaderData.allScheduleStreams.map((st) => [st.ref_id, st]),
  );

  return (
    <LeafPanel
      key={`schedule-event-in-day-${loaderData.scheduleEventInDay.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityNotEditable={!corePropertyEditable}
      entityArchived={loaderData.scheduleEventInDay.archived}
      returnLocation={`/app/workspace/calendar?${query}`}
    >
      <TimeEventParamsSource
        startDate={startDate}
        startTimeInDay={startTimeInDay}
        durationMins={durationMins}
      />
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
                    disabled: !corePropertyEditable,
                  }),
                  ActionSingle({
                    text: "Change Stream",
                    value: "change-schedule-stream",
                    disabled: !corePropertyEditable,
                  }),
                ],
              }),
            ]}
          />
        }
      >
        <Stack spacing={2} useFlexGap>
          <input
            type="hidden"
            name="userTimezone"
            value={topLevelInfo.user.timezone}
          />
          <FormControl fullWidth>
            <InputLabel id="scheduleStreamRefId">Schedule Stream</InputLabel>
            <ScheduleStreamSelect
              labelId="scheduleStreamRefId"
              label="Schedule Stream"
              name="scheduleStreamRefId"
              readOnly={!inputsEnabled || !corePropertyEditable}
              allScheduleStreams={loaderData.allScheduleStreams}
              defaultValue={
                allScheduleStreamsByRefId.get(
                  loaderData.scheduleEventInDay.schedule_stream_ref_id,
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
              readOnly={!inputsEnabled || !corePropertyEditable}
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
              notched
              label="startDate"
              name="startDate"
              readOnly={!inputsEnabled || !corePropertyEditable}
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
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
              readOnly={!inputsEnabled || !corePropertyEditable}
              value={startTimeInDay}
              onChange={(e) => setStartTimeInDay(e.target.value)}
            />

            <FieldError
              actionResult={actionData}
              fieldName="/start_time_in_day"
            />
          </FormControl>

          <Stack spacing={2} direction="row">
            <ButtonGroup
              variant="outlined"
              disabled={!inputsEnabled || !corePropertyEditable}
            >
              <Button
                disabled={!inputsEnabled || !corePropertyEditable}
                variant={durationMins === 15 ? "contained" : "outlined"}
                onClick={() => setDurationMins(15)}
              >
                15m
              </Button>
              <Button
                disabled={!inputsEnabled || !corePropertyEditable}
                variant={durationMins === 30 ? "contained" : "outlined"}
                onClick={() => setDurationMins(30)}
              >
                30m
              </Button>
              <Button
                disabled={!inputsEnabled || !corePropertyEditable}
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
                readOnly={!inputsEnabled || !corePropertyEditable}
                value={durationMins}
                onChange={(e) => {
                  if (Number.isNaN(parseInt(e.target.value, 10))) {
                    setDurationMins(0);
                    e.preventDefault();
                    return;
                  }

                  return setDurationMins(parseInt(e.target.value, 10));
                }}
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
        {!(loaderData.note && !loaderData.note.archived) && (
          <CardActions>
            <ButtonGroup>
              <Button
                variant="contained"
                disabled={!inputsEnabled || !corePropertyEditable}
                type="submit"
                name="intent"
                value="create-note"
              >
                Create Note
              </Button>
            </ButtonGroup>
          </CardActions>
        )}

        {loaderData.note && !loaderData.note.archived && (
          <>
            <EntityNoteEditor
              initialNote={loaderData.note}
              inputsEnabled={inputsEnabled && corePropertyEditable}
            />
          </>
        )}
      </Card>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  (params) => `/app/workspace/calendar/schedule/event-in-day/${params.id}`,
  ParamsSchema,
  {
    notFound: (params) => `Could not find event in day #${params.id}!`,
    error: (params) =>
      `There was an error loading event in day #${params.id}! Please try again!`,
  },
);

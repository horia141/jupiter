import type { ScheduleStreamSummary } from "@jupiter/webapi-client";
import { ApiError } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
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
  useNavigation,
  useSearchParams,
  useTransition,
} from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";

import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { ScheduleStreamSelect } from "~/components/schedule-stream-select";
import { TimeEventParamsSource } from "~/components/time-event-params-source";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { timeEventInDayBlockParamsToUtc } from "~/logic/domain/time-event";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const QuerySchema = {
  date: z
    .string()
    .regex(/[0-9][0-9][0-9][0-9][-][0-9][0-9][-][0-9][0-9]/)
    .optional(),
  initialStartDate: z
    .string()
    .regex(/[0-9][0-9][0-9][0-9][-][0-9][0-9][-][0-9][0-9]/)
    .optional(),
  initialStartTimeInDay: z.string().optional(),
};

const CreateFormSchema = {
  scheduleStreamRefId: z.string(),
  userTimezone: z.string(),
  name: z.string(),
  startDate: z.string(),
  startTimeInDay: z.string().optional(),
  durationMins: z.string().transform((v) => parseInt(v, 10)),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const query = parseQuery(request, QuerySchema);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_schedule_streams: true,
  });

  return json({
    date: query.date,
    allScheduleStreams:
      summaryResponse.schedule_streams as Array<ScheduleStreamSummary>,
  });
}

export async function action({ request }: ActionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, CreateFormSchema);
  const url = new URL(request.url);

  try {
    const { startDate, startTimeInDay } = timeEventInDayBlockParamsToUtc(
      form,
      form.userTimezone,
    );
    const response = await apiClient.eventInDay.scheduleEventInDayCreate({
      schedule_stream_ref_id: form.scheduleStreamRefId,
      name: form.name,
      start_date: startDate,
      start_time_in_day: startTimeInDay ?? "",
      duration_mins: form.durationMins,
    });

    return redirect(
      `/app/workspace/calendar/schedule/event-in-day/${response.new_schedule_event_in_day.ref_id}?${url.searchParams}`,
    );
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

export default function ScheduleEventInDayNew() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const navigation = useNavigation();
  const [query] = useSearchParams();

  const inputsEnabled = navigation.state === "idle";

  const rightNow = DateTime.local({ zone: topLevelInfo.user.timezone });

  const [startDate, setStartDate] = useState(rightNow.toFormat("yyyy-MM-dd"));
  const [startTimeInDay, setStartTimeInDay] = useState(
    rightNow.toFormat("HH:mm"),
  );
  const [durationMins, setDurationMins] = useState(30);

  useEffect(() => {
    if (query.get("sourceStartDate") && query.get("sourceStartTimeInDay")) {
      setStartDate(query.get("sourceStartDate")!);
      setStartTimeInDay(query.get("sourceStartTimeInDay")!);
    }
    if (query.get("sourceDurationMins")) {
      setDurationMins(parseInt(query.get("sourceDurationMins")!, 10));
    }
  }, [query]);

  return (
    <LeafPanel
      key="schedule-event-in-day/new"
      returnLocation={`/app/workspace/calendar?${query}`}
      inputsEnabled={inputsEnabled}
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
              ActionSingle({
                text: "Create",
                value: "create",
                highlight: true,
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
              readOnly={!inputsEnabled}
              allScheduleStreams={loaderData.allScheduleStreams}
              defaultValue={loaderData.allScheduleStreams[0]}
            />
            <FieldError
              actionResult={actionData}
              fieldName="/schedule_stream_ref_id"
            />
          </FormControl>
          <FormControl fullWidth>
            <InputLabel id="name">Name</InputLabel>
            <OutlinedInput label="name" name="name" readOnly={!inputsEnabled} />
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
              readOnly={!inputsEnabled}
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
              readOnly={!inputsEnabled}
              value={startTimeInDay}
              onChange={(e) => setStartTimeInDay(e.target.value)}
            />

            <FieldError
              actionResult={actionData}
              fieldName="/start_time_in_day"
            />
          </FormControl>

          <Stack spacing={2} direction="row">
            <ButtonGroup variant="outlined" disabled={!inputsEnabled}>
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
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  () => `/app/workspace/calendar?${useSearchParams()}`,
  () => `There was an error creating the event in day! Please try again!`,
);

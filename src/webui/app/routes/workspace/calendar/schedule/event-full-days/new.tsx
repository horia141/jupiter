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
  useSearchParams,
  useTransition,
} from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext, useState } from "react";
import { z } from "zod";
import { parseForm, parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { ScheduleStreamSelect } from "~/components/schedule-stream-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const QuerySchema = {
  date: z
    .string()
    .regex(/[0-9][0-9][0-9][0-9][-][0-9][0-9][-][0-9][0-9]/)
    .optional(),
};

const CreateFormSchema = {
  scheduleStreamRefId: z.string(),
  name: z.string(),
  startDate: z.string(),
  durationDays: z.string().transform((v) => parseInt(v, 10)),
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
    const response = await apiClient.eventFullDays.scheduleEventFullDaysCreate({
      schedule_stream_ref_id: form.scheduleStreamRefId,
      name: form.name,
      start_date: form.startDate,
      duration_days: form.durationDays,
    });

    return redirect(
      `/workspace/calendar/schedule/event-full-days/${response.new_schedule_event_full_days.ref_id}?${url.searchParams}`
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

export default function ScheduleEventFullDaysNew() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const transition = useTransition();
  const [query] = useSearchParams();

  const inputsEnabled = transition.state === "idle";

  const [durationDays, setDurationDays] = useState(1);

  return (
    <LeafPanel
      key="schedule-event-full-days/new"
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
              defaultValue={loaderData.date}
            />

            <FieldError actionResult={actionData} fieldName="/start_date" />
          </FormControl>

          <Stack spacing={2} direction="row">
            <ButtonGroup variant="outlined" disabled={!inputsEnabled}>
              <Button
                disabled={!inputsEnabled}
                variant={durationDays === 1 ? "contained" : "outlined"}
                onClick={() => setDurationDays(1)}
              >
                1d
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
    </LeafPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the event full days! Please try again!`
);

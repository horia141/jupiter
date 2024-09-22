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
import { DateTime } from "luxon";
import { useContext, useState } from "react";
import { z } from "zod";
import { parseForm, parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { timeEventInDayBlockParamsToUtc } from "~/logic/domain/time-event";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const QuerySchema = {
  inboxTaskRefId: z.string(),
  date: z
    .string()
    .regex(/[0-9][0-9][0-9][0-9][-][0-9][0-9][-][0-9][0-9]/)
    .optional(),
};

const CreateFormSchema = {
  userTimezone: z.string(),
  startDate: z.string(),
  startTimeInDay: z.string().optional(),
  durationMins: z.string().transform((v) => parseInt(v, 10)),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const query = parseQuery(request, QuerySchema);

  const summaryResponse = await getLoggedInApiClient(
    session
  ).inboxTasks.inboxTaskLoad({
    ref_id: query.inboxTaskRefId,
    allow_archived: true,
  });

  return json({
    date: query.date,
    inboxTask: summaryResponse.inbox_task,
  });
}

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const query = parseQuery(request, QuerySchema);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const { startDate, startTimeInDay } = timeEventInDayBlockParamsToUtc(
      form,
      form.userTimezone
    );

    await getLoggedInApiClient(
      session
    ).inDayBlock.timeEventInDayBlockCreateForInboxTask({
      inbox_task_ref_id: query.inboxTaskRefId,
      start_date: startDate,
      start_time_in_day: startTimeInDay ?? "",
      duration_mins: form.durationMins,
    });

    return redirect(`/workspace/inbox-tasks/${query.inboxTaskRefId}`);
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

export default function TimeEventInDayBlockCreateForInboxTask() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const transition = useTransition();
  const [query] = useSearchParams();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.inboxTask.archived;

  const rightNow = DateTime.now();

  const [durationMins, setDurationMins] = useState(30);

  return (
    <LeafPanel
      key="time-event-in-day-block/new"
      returnLocation={`/workspace/calendar?${query}`}
    >
      <GlobalError actionResult={actionData} />
      <SectionCardNew
        id="time-event-in-day-block-properties"
        title="Properties"
        actions={
          <SectionActions
            id="time-event-in-day-block-properties"
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
            <InputLabel id="name">Name</InputLabel>
            <OutlinedInput
              label="name"
              name="name"
              defaultValue={loaderData.inboxTask.name}
              readOnly={true}
            />
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
              defaultValue={loaderData.date}
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
              defaultValue={rightNow.toFormat("HH:mm")}
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

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the event in day! Please try again!`
);

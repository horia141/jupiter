import { ApiError, TimeEventNamespace } from "@jupiter/webapi-client";
import {
  Box,
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
  useParams,
  useSearchParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
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
import { TimeEventSourceLink } from "~/components/time-event-source-link";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import {
  isTimeEventInDayBlockEditable,
  timeEventInDayBlockParamsToTimezone,
  timeEventInDayBlockParamsToUtc,
} from "~/logic/domain/time-event";
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
    userTimezone: z.string(),
    startDate: z.string(),
    startTimeInDay: z.string().optional(),
    durationMins: z.string().transform((v) => parseInt(v, 10)),
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

  try {
    const response = await getLoggedInApiClient(
      session
    ).inDayBlock.timeEventInDayBlockLoad({
      ref_id: id,
      allow_archived: true,
    });

    return json({
      inDayBlock: response.in_day_block,
      scheduleEvent: response.schedule_event,
      inboxTask: response.inbox_task,
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
        const { startDate, startTimeInDay } = timeEventInDayBlockParamsToUtc(
          form,
          form.userTimezone
        );
        await getLoggedInApiClient(
          session
        ).inDayBlock.timeEventInDayBlockUpdate({
          ref_id: id,
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
        return redirect(
          `/workspace/calendar/time-event/in-day-block/${id}?${url.searchParams}`
        );
      }

      case "archive": {
        await getLoggedInApiClient(
          session
        ).inDayBlock.timeEventInDayBlockArchive({
          ref_id: id,
        });
        return redirect(
          `/workspace/calendar/time-event/in-day-block/${id}?${url.searchParams}`
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

export default function TimeEventInDayBlockViewOne() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const transition = useTransition();
  const [query] = useSearchParams();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.inDayBlock.archived;
  const corePropertyEditable = isTimeEventInDayBlockEditable(
    loaderData.inDayBlock.namespace
  );

  const [durationMins, setDurationMins] = useState(
    loaderData.inDayBlock.duration_mins
  );
  useEffect(() => {
    setDurationMins(loaderData.inDayBlock.duration_mins);
  }, [loaderData.inDayBlock.duration_mins]);

  let name = null;
  switch (loaderData.inDayBlock.namespace) {
    case TimeEventNamespace.SCHEDULE_EVENT_IN_DAY:
      name = loaderData.scheduleEvent!.name;
      break;

    case TimeEventNamespace.INBOX_TASK:
      name = loaderData.inboxTask!.name;
      break;

    default:
      throw new Error("Unknown namespace");
  }

  const { startDate, startTimeInDay } = timeEventInDayBlockParamsToTimezone(
    {
      startDate: loaderData.inDayBlock.start_date,
      startTimeInDay: loaderData.inDayBlock.start_time_in_day,
    },
    topLevelInfo.user.timezone
  );

  return (
    <LeafPanel
      key={`time-event-in-day-block-${loaderData.inDayBlock.ref_id}`}
      showArchiveButton={corePropertyEditable}
      enableArchiveButton={inputsEnabled && corePropertyEditable}
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
            inputsEnabled={inputsEnabled && corePropertyEditable}
            actions={[
              ActionMultipleSpread({
                actions: [
                  ActionSingle({
                    text: "Save",
                    value: "update",
                    highlight: true,
                  }),
                ],
              }),
            ]}
          />
        }
      >
        <Stack spacing={2} useFlexGap>
          <Box sx={{ display: "flex", flexDirection: "row", gap: "0.25rem" }}>
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
                readOnly={true}
                defaultValue={name}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            <TimeEventSourceLink timeEvent={loaderData.inDayBlock} />
          </Box>

          <FormControl fullWidth>
            <InputLabel id="startDate" shrink margin="dense">
              Start Date
            </InputLabel>
            <OutlinedInput
              type="date"
              label="startDate"
              name="startDate"
              readOnly={!(inputsEnabled && corePropertyEditable)}
              defaultValue={startDate}
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
              readOnly={!(inputsEnabled && corePropertyEditable)}
              defaultValue={startTimeInDay}
            />

            <FieldError
              actionResult={actionData}
              fieldName="/start_time_in_day"
            />
          </FormControl>

          <Stack spacing={2} direction="row">
            <ButtonGroup
              variant="outlined"
              disabled={!(inputsEnabled && corePropertyEditable)}
            >
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
                readOnly={!(inputsEnabled && corePropertyEditable)}
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

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find time event in day block #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading time event in day block #${
      useParams().id
    }. Please try again!`
);

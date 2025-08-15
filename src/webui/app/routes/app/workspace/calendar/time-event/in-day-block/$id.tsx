import type { BigPlanSummary, ProjectSummary } from "@jupiter/webapi-client";
import {
  ApiError,
  Difficulty,
  Eisen,
  InboxTaskSource,
  InboxTaskStatus,
  TimeEventNamespace,
} from "@jupiter/webapi-client";
import {
  Box,
  Button,
  ButtonGroup,
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
import { CheckboxAsString, parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { InboxTaskPropertiesEditor } from "~/components/domain/concept/inbox-task/inbox-task-properties-editor";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionMultipleSpread,
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCard } from "~/components/infra/section-card";
import { TimeEventParamsSource } from "~/components/domain/application/calendar/time-event-params-source";
import { TimeEventSourceLink } from "~/components/domain/application/calendar/time-event-source-link";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { saveScoreAction } from "~/logic/domain/gamification/scores.server";
import { isInboxTaskCoreFieldEditable } from "~/logic/domain/inbox-task";
import { allowUserChanges } from "~/logic/domain/inbox-task-source";
import {
  isTimeEventInDayBlockEditable,
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

const UpdateFormInboxTaskSchema = {
  inboxTaskRefId: z.string(),
  inboxTaskSource: z.nativeEnum(InboxTaskSource),
  inboxTaskName: z.string(),
  inboxTaskProject: z.string().optional(),
  inboxTaskBigPlan: z.string().optional(),
  inboxTaskStatus: z.nativeEnum(InboxTaskStatus),
  inboxTaskIsKey: CheckboxAsString,
  inboxTaskEisen: z.nativeEnum(Eisen),
  inboxTaskDifficulty: z.nativeEnum(Difficulty),
  inboxTaskActionableDate: z.string().optional(),
  inboxTaskDueDate: z.string().optional(),
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
  z.object({
    intent: z.literal("remove"),
  }),
  z.object({
    intent: z.literal("inbox-task-mark-done"),
    ...UpdateFormInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("inbox-task-mark-not-done"),
    ...UpdateFormInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("inbox-task-start"),
    ...UpdateFormInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("inbox-task-restart"),
    ...UpdateFormInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("inbox-task-block"),
    ...UpdateFormInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("inbox-task-stop"),
    ...UpdateFormInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("inbox-task-reactivate"),
    ...UpdateFormInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("inbox-task-update"),
    ...UpdateFormInboxTaskSchema,
  }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    allow_archived: false,
    include_workspace: true,
    include_projects: true,
    include_big_plans: true,
  });

  try {
    const response = await apiClient.inDayBlock.timeEventInDayBlockLoad({
      ref_id: id,
      allow_archived: true,
    });

    let inboxTaskResult = null;
    if (response.inbox_task) {
      inboxTaskResult = await apiClient.inboxTasks.inboxTaskLoad({
        ref_id: response.inbox_task.ref_id,
        allow_archived: true,
      });
    }

    return json({
      rootProject: summaryResponse.root_project as ProjectSummary,
      allProjects: summaryResponse.projects as Array<ProjectSummary>,
      allBigPlans: summaryResponse.big_plans as Array<BigPlanSummary>,
      inDayBlock: response.in_day_block,
      scheduleEvent: response.schedule_event,
      inboxTask: response.inbox_task,
      inboxTaskInfo: inboxTaskResult,
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
        await apiClient.inDayBlock.timeEventInDayBlockUpdate({
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
        return redirect(`/app/workspace/calendar?${url.searchParams}`);
      }

      case "archive": {
        await apiClient.inDayBlock.timeEventInDayBlockArchive({
          ref_id: id,
        });
        return redirect(`/app/workspace/calendar?${url.searchParams}`);
      }

      case "remove": {
        await apiClient.inDayBlock.timeEventInDayBlockRemove({
          ref_id: id,
        });
        return redirect(`/app/workspace/calendar?${url.searchParams}`);
      }

      case "inbox-task-mark-done":
      case "inbox-task-mark-not-done":
      case "inbox-task-start":
      case "inbox-task-restart":
      case "inbox-task-block":
      case "inbox-task-stop":
      case "inbox-task-reactivate":
      case "inbox-task-update": {
        const corePropertyEditable = isInboxTaskCoreFieldEditable(
          form.inboxTaskSource,
        );

        let status = form.inboxTaskStatus;
        if (form.intent === "inbox-task-mark-done") {
          status = InboxTaskStatus.DONE;
        } else if (form.intent === "inbox-task-mark-not-done") {
          status = InboxTaskStatus.NOT_DONE;
        } else if (form.intent === "inbox-task-start") {
          status = InboxTaskStatus.IN_PROGRESS;
        } else if (form.intent === "inbox-task-restart") {
          status = InboxTaskStatus.IN_PROGRESS;
        } else if (form.intent === "inbox-task-block") {
          status = InboxTaskStatus.BLOCKED;
        } else if (form.intent === "inbox-task-stop") {
          status = allowUserChanges(form.inboxTaskSource)
            ? InboxTaskStatus.NOT_STARTED
            : InboxTaskStatus.NOT_STARTED_GEN;
        } else if (form.intent === "inbox-task-reactivate") {
          status = allowUserChanges(form.inboxTaskSource)
            ? InboxTaskStatus.NOT_STARTED
            : InboxTaskStatus.NOT_STARTED_GEN;
        }

        const result = await apiClient.inboxTasks.inboxTaskUpdate({
          ref_id: form.inboxTaskRefId,
          name: corePropertyEditable
            ? {
                should_change: true,
                value: form.inboxTaskName,
              }
            : { should_change: false },
          status: {
            should_change: true,
            value: status,
          },
          project_ref_id: {
            should_change: true,
            value: form.inboxTaskProject,
          },
          big_plan_ref_id: {
            should_change: form.inboxTaskBigPlan !== undefined,
            value:
              form.inboxTaskBigPlan !== undefined &&
              form.inboxTaskBigPlan !== "none"
                ? form.inboxTaskBigPlan
                : undefined,
          },
          is_key: corePropertyEditable
            ? {
                should_change: true,
                value: form.inboxTaskIsKey,
              }
            : { should_change: false },
          eisen: corePropertyEditable
            ? {
                should_change: true,
                value: form.inboxTaskEisen,
              }
            : { should_change: false },
          difficulty: corePropertyEditable
            ? {
                should_change: true,
                value: form.inboxTaskDifficulty,
              }
            : { should_change: false },
          actionable_date: {
            should_change: true,
            value:
              form.inboxTaskActionableDate !== undefined &&
              form.inboxTaskActionableDate !== ""
                ? form.inboxTaskActionableDate
                : undefined,
          },
          due_date: {
            should_change: true,
            value:
              form.inboxTaskDueDate !== undefined &&
              form.inboxTaskDueDate !== ""
                ? form.inboxTaskDueDate
                : undefined,
          },
        });

        if (result.record_score_result) {
          return redirect(`/app/workspace/calendar?${url.searchParams}`, {
            headers: {
              "Set-Cookie": await saveScoreAction(result.record_score_result),
            },
          });
        }

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

export default function TimeEventInDayBlockViewOne() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const navigation = useNavigation();
  const [query] = useSearchParams();

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.inDayBlock.archived;
  const corePropertyEditable = isTimeEventInDayBlockEditable(
    loaderData.inDayBlock.namespace,
  );

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

  const blockParamsInTz = timeEventInDayBlockParamsToTimezone(
    {
      startDate: loaderData.inDayBlock.start_date,
      startTimeInDay: loaderData.inDayBlock.start_time_in_day,
    },
    topLevelInfo.user.timezone,
  );
  const [startDate, setStartDate] = useState(blockParamsInTz.startDate);
  const [startTimeInDay, setStartTimeInDay] = useState(
    blockParamsInTz.startTimeInDay!,
  );
  const [durationMins, setDurationMins] = useState(
    loaderData.inDayBlock.duration_mins,
  );
  useEffect(() => {
    const blockParamsInTz = timeEventInDayBlockParamsToTimezone(
      {
        startDate: loaderData.inDayBlock.start_date,
        startTimeInDay: loaderData.inDayBlock.start_time_in_day,
      },
      topLevelInfo.user.timezone,
    );
    setStartDate(blockParamsInTz.startDate);
    setStartTimeInDay(blockParamsInTz.startTimeInDay!);
    setDurationMins(loaderData.inDayBlock.duration_mins);
  }, [loaderData.inDayBlock, topLevelInfo.user.timezone]);

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

  return (
    <LeafPanel
      key={`time-event-in-day-block-${loaderData.inDayBlock.ref_id}`}
      fakeKey={`time-event-in-day-block-${loaderData.inDayBlock.ref_id}`}
      showArchiveAndRemoveButton={corePropertyEditable}
      inputsEnabled={inputsEnabled}
      entityNotEditable={!corePropertyEditable}
      entityArchived={loaderData.inDayBlock.archived}
      returnLocation={`/app/workspace/calendar?${query}`}
    >
      <TimeEventParamsSource
        startDate={startDate}
        startTimeInDay={startTimeInDay}
        durationMins={durationMins}
      />
      <GlobalError actionResult={actionData} />
      <SectionCard
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
            notched
            label="startDate"
            name="startDate"
            readOnly={!(inputsEnabled && corePropertyEditable)}
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
            readOnly={!(inputsEnabled && corePropertyEditable)}
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

            <FieldError actionResult={actionData} fieldName="/duration_mins" />
          </FormControl>
        </Stack>
      </SectionCard>

      {loaderData.inboxTask && (
        <InboxTaskPropertiesEditor
          title="Inbox Task"
          showLinkToInboxTask
          intentPrefix="inbox-task"
          namePrefix="inboxTask"
          topLevelInfo={topLevelInfo}
          rootProject={loaderData.rootProject}
          allProjects={loaderData.allProjects}
          allBigPlans={loaderData.allBigPlans}
          inputsEnabled={inputsEnabled && !loaderData.inboxTask.archived}
          inboxTask={loaderData.inboxTask}
          inboxTaskInfo={loaderData.inboxTaskInfo!}
          actionData={actionData}
        />
      )}
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  (params) => `/app/workspace/calendar/time-event/in-day-block/${params.id}`,
  ParamsSchema,
  {
    notFound: (params) =>
      `Could not find time event in day block #${params.id}!`,
    error: (params) =>
      `There was an error loading time event in day block #${params.id}! Please try again!`,
  },
);

import type {
  BigPlanSummary,
  ProjectSummary,
  Workspace,
} from "@jupiter/webapi-client";
import {
  ApiError,
  Difficulty,
  Eisen,
  InboxTaskSource,
  InboxTaskStatus,
  NoteDomain,
  TimePlanActivityTarget,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import { Button, ButtonGroup, Card, CardActions } from "@mui/material";
import {
  json,
  redirect,
  type ActionArgs,
  type LoaderArgs,
} from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { InboxTaskPropertiesEditor } from "~/components/entities/inbox-task-properties-editor";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { makeLeafCatchBoundary } from "~/components/infra/catch-boundary";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { TimeEventInDayBlockStack } from "~/components/time-event-in-day-block-stack";
import { TimePlanActivityList } from "~/components/time-plan-activity-list";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { saveScoreAction } from "~/logic/domain/gamification/scores.server";
import { isInboxTaskCoreFieldEditable } from "~/logic/domain/inbox-task";
import { allowUserChanges } from "~/logic/domain/inbox-task-source";
import {
  sortInboxTaskTimeEventsNaturally,
  timeEventInDayBlockToTimezone,
} from "~/logic/domain/time-event";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

const CommonParamsSchema = {
  source: z.nativeEnum(InboxTaskSource),
  name: z.string(),
  status: z.nativeEnum(InboxTaskStatus),
  project: z.string().optional(),
  bigPlan: z.string().optional(),
  eisen: z.nativeEnum(Eisen),
  difficulty: z.nativeEnum(Difficulty),
  actionableDate: z.string().optional(),
  dueDate: z.string().optional(),
};

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("mark-done"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("mark-not-done"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("start"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("restart"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("block"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("stop"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("reactivate"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("update"),
    ...CommonParamsSchema,
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

export async function loader({ request, params }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    allow_archived: false,
    include_workspace: true,
    include_projects: true,
    include_big_plans: true,
  });

  try {
    const result = await apiClient.inboxTasks.inboxTaskLoad({
      ref_id: id,
      allow_archived: true,
    });

    const workspace = summaryResponse.workspace as Workspace;
    let timePlanEntries = undefined;
    if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.TIME_PLANS)) {
      const timePlanActivitiesResult =
        await apiClient.activity.timePlanActivityFindForTarget({
          allow_archived: true,
          target: TimePlanActivityTarget.INBOX_TASK,
          target_ref_id: id,
        });
      timePlanEntries = timePlanActivitiesResult.entries;
    }

    return json({
      info: result,
      timePlanEntries: timePlanEntries,
      rootProject: summaryResponse.root_project as ProjectSummary,
      allProjects: summaryResponse.projects as Array<ProjectSummary>,
      allBigPlans: summaryResponse.big_plans as Array<BigPlanSummary>,
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
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "mark-done":
      case "mark-not-done":
      case "start":
      case "restart":
      case "block":
      case "stop":
      case "reactivate":
      case "update": {
        let status = form.status;
        const corePropertyEditable = isInboxTaskCoreFieldEditable(form.source);

        if (form.intent === "mark-done") {
          status = InboxTaskStatus.DONE;
        } else if (form.intent === "mark-not-done") {
          status = InboxTaskStatus.NOT_DONE;
        } else if (form.intent === "start") {
          status = InboxTaskStatus.IN_PROGRESS;
        } else if (form.intent === "restart") {
          status = InboxTaskStatus.IN_PROGRESS;
        } else if (form.intent === "block") {
          status = InboxTaskStatus.BLOCKED;
        } else if (form.intent === "stop") {
          status = allowUserChanges(form.source)
            ? InboxTaskStatus.NOT_STARTED
            : InboxTaskStatus.NOT_STARTED_GEN;
        } else if (form.intent === "reactivate") {
          status = allowUserChanges(form.source)
            ? InboxTaskStatus.NOT_STARTED
            : InboxTaskStatus.NOT_STARTED_GEN;
        }

        const result = await apiClient.inboxTasks.inboxTaskUpdate({
          ref_id: id,
          name: corePropertyEditable
            ? {
                should_change: true,
                value: form.name,
              }
            : { should_change: false },
          status: {
            should_change: true,
            value: status,
          },
          project_ref_id: {
            should_change: form.project !== undefined,
            value: form.project,
          },
          big_plan_ref_id: {
            should_change: form.bigPlan !== undefined,
            value:
              form.bigPlan !== undefined && form.bigPlan !== "none"
                ? form.bigPlan
                : undefined,
          },
          eisen: corePropertyEditable
            ? {
                should_change: true,
                value: form.eisen,
              }
            : { should_change: false },
          difficulty: corePropertyEditable
            ? {
                should_change: true,
                value: form.difficulty,
              }
            : { should_change: false },
          actionable_date: {
            should_change: true,
            value:
              form.actionableDate !== undefined && form.actionableDate !== ""
                ? form.actionableDate
                : undefined,
          },
          due_date: {
            should_change: true,
            value:
              form.dueDate !== undefined && form.dueDate !== ""
                ? form.dueDate
                : undefined,
          },
        });

        if (result.record_score_result) {
          return redirect(`/workspace/inbox-tasks`, {
            headers: {
              "Set-Cookie": await saveScoreAction(result.record_score_result),
            },
          });
        }

        return redirect(`/workspace/inbox-tasks`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.INBOX_TASK,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/workspace/inbox-tasks/${id}`);
      }

      case "archive": {
        await apiClient.inboxTasks.inboxTaskArchive({
          ref_id: id,
        });

        return redirect(`/workspace/inbox-tasks`);
      }

      case "remove": {
        await apiClient.inboxTasks.inboxTaskRemove({
          ref_id: id,
        });

        return redirect(`/workspace/inbox-tasks`);
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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function InboxTask() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const topLevelInfo = useContext(TopLevelInfoContext);
  const info = loaderData.info;
  const inboxTask = loaderData.info.inbox_task;

  const inputsEnabled = transition.state === "idle" && !inboxTask.archived;

  const corePropertyEditable = isInboxTaskCoreFieldEditable(inboxTask.source);

  const inboxTasksByRefId = new Map();
  inboxTasksByRefId.set(
    loaderData.info.inbox_task.ref_id,
    loaderData.info.inbox_task
  );

  const timePlanActivities = loaderData.timePlanEntries?.map(
    (entry) => entry.time_plan_activity
  );
  const timePlansByRefId = new Map();
  if (loaderData.timePlanEntries) {
    for (const entry of loaderData.timePlanEntries) {
      timePlansByRefId.set(entry.time_plan.ref_id, entry.time_plan);
    }
  }

  const timeEventsByRefId = new Map();
  timeEventsByRefId.set(
    `it:${loaderData.info.inbox_task.ref_id}`,
    loaderData.info.time_event_blocks
  );

  const timeEventEntries = loaderData.info.time_event_blocks.map((block) => ({
    time_event_in_tz: timeEventInDayBlockToTimezone(
      block,
      topLevelInfo.user.timezone
    ),
    entry: {
      inbox_task: loaderData.info.inbox_task,
      time_events: [block],
    },
  }));
  const sortedTimeEventEntries =
    sortInboxTaskTimeEventsNaturally(timeEventEntries);

  return (
    <LeafPanel
      key={`inbox-task-${inboxTask.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={inboxTask.archived}
      entityNotEditable={!corePropertyEditable}
      returnLocation="/workspace/inbox-tasks"
    >
      <GlobalError actionResult={actionData} />
      <InboxTaskPropertiesEditor
        title="Properties"
        topLevelInfo={topLevelInfo}
        rootProject={loaderData.rootProject}
        allProjects={loaderData.allProjects}
        allBigPlans={loaderData.allBigPlans}
        inputsEnabled={inputsEnabled}
        inboxTask={inboxTask}
        inboxTaskInfo={info}
        actionData={actionData}
      />

      <Card>
        {!loaderData.info.note && (
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

        {loaderData.info.note && (
          <>
            <EntityNoteEditor
              initialNote={loaderData.info.note}
              inputsEnabled={inputsEnabled}
            />
          </>
        )}
      </Card>

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.SCHEDULE
      ) && (
        <TimeEventInDayBlockStack
          topLevelInfo={topLevelInfo}
          inputsEnabled={inputsEnabled}
          title="Time Events"
          createLocation={`/workspace/calendar/time-event/in-day-block/new-for-inbox-task?inboxTaskRefId=${loaderData.info.inbox_task.ref_id}`}
          entries={sortedTimeEventEntries}
        />
      )}

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.TIME_PLANS
      ) &&
        timePlanActivities && (
          <SectionCardNew
            id="inbox-task-time-plan-activities"
            title="Time Plan Activities"
          >
            <TimePlanActivityList
              topLevelInfo={topLevelInfo}
              activities={timePlanActivities}
              timePlansByRefId={timePlansByRefId}
              inboxTasksByRefId={inboxTasksByRefId}
              bigPlansByRefId={new Map()}
              activityDoneness={{}}
              timeEventsByRefId={timeEventsByRefId}
              fullInfo={false}
            />
          </SectionCardNew>
        )}
    </LeafPanel>
  );
}

export const CatchBoundary = makeLeafCatchBoundary(
  "/workspace/inbox-tasks",
  () => `Could not find inbox task #${useParams().id}!`
);

export const ErrorBoundary = makeLeafErrorBoundary(
  "/workspace/inbox-tasks",
  () =>
    `There was an error loading inbox task #${
      useParams().id
    }! Please try again!`
);

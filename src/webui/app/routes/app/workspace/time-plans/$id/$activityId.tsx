import type {
  BigPlanSummary,
  ProjectSummary,
  TimePlan,
} from "@jupiter/webapi-client";
import {
  ApiError,
  Difficulty,
  Eisen,
  InboxTaskSource,
  InboxTaskStatus,
  RecurringTaskPeriod,
  TimePlanActivityFeasability,
  TimePlanActivityKind,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import { FormControl, FormLabel, Stack } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  useActionData,
  useNavigation,
  useParams,
  useRouteLoaderData,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { CheckboxAsString, parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { BigPlanStack } from "~/components/domain/concept/big-plan/big-plan-stack";
import { InboxTaskPropertiesEditor } from "~/components/domain/concept/inbox-task/inbox-task-properties-editor";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionSingle,
  NavMultipleSpread,
  NavSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCard } from "~/components/infra/section-card";
import { TimeEventInDayBlockStack } from "~/components/domain/application/calendar/time-event-in-day-block-stack";
import { TimePlanActivityFeasabilitySelect } from "~/components/domain/concept/time-plan/time-plan-activity-feasability-select";
import { TimePlanActivitKindSelect } from "~/components/domain/concept/time-plan/time-plan-activity-kind-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { saveScoreAction } from "~/logic/domain/gamification/scores.server";
import { isInboxTaskCoreFieldEditable } from "~/logic/domain/inbox-task";
import { allowUserChanges } from "~/logic/domain/inbox-task-source";
import {
  sortInboxTaskTimeEventsNaturally,
  timeEventInDayBlockToTimezone,
} from "~/logic/domain/time-event";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({
  id: z.string(),
  activityId: z.string(),
});

const UpdateFormTargetInboxTaskSchema = {
  targetInboxTaskRefId: z.string(),
  targetInboxTaskSource: z.nativeEnum(InboxTaskSource),
  targetInboxTaskName: z.string(),
  targetInboxTaskProject: z.string().optional(),
  targetInboxTaskBigPlan: z.string().optional(),
  targetInboxTaskIsKey: CheckboxAsString,
  targetInboxTaskStatus: z.nativeEnum(InboxTaskStatus),
  targetInboxTaskEisen: z.nativeEnum(Eisen),
  targetInboxTaskDifficulty: z.nativeEnum(Difficulty),
  targetInboxTaskActionableDate: z.string().optional(),
  targetInboxTaskDueDate: z.string().optional(),
};

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    kind: z.nativeEnum(TimePlanActivityKind),
    feasability: z.nativeEnum(TimePlanActivityFeasability),
  }),
  z.object({
    intent: z.literal("archive"),
  }),
  z.object({
    intent: z.literal("remove"),
  }),
  z.object({
    intent: z.literal("target-inbox-task-mark-done"),
    ...UpdateFormTargetInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("target-inbox-task-mark-not-done"),
    ...UpdateFormTargetInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("target-inbox-task-start"),
    ...UpdateFormTargetInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("target-inbox-task-restart"),
    ...UpdateFormTargetInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("target-inbox-task-block"),
    ...UpdateFormTargetInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("target-inbox-task-stop"),
    ...UpdateFormTargetInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("target-inbox-task-reactivate"),
    ...UpdateFormTargetInboxTaskSchema,
  }),
  z.object({
    intent: z.literal("target-inbox-task-update"),
    ...UpdateFormTargetInboxTaskSchema,
  }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { activityId } = parseParams(params, ParamsSchema);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    allow_archived: false,
    include_workspace: true,
    include_projects: true,
    include_big_plans: true,
  });

  try {
    const result = await apiClient.activity.timePlanActivityLoad({
      ref_id: activityId,
      allow_archived: true,
    });

    let inboxTaskResult = null;
    if (result.target_inbox_task) {
      inboxTaskResult = await apiClient.inboxTasks.inboxTaskLoad({
        ref_id: result.target_inbox_task.ref_id,
        allow_archived: true,
      });
    }

    return json({
      rootProject: summaryResponse.root_project as ProjectSummary,
      allProjects: summaryResponse.projects as Array<ProjectSummary>,
      allBigPlans: summaryResponse.big_plans as Array<BigPlanSummary>,
      timePlanActivity: result.time_plan_activity,
      targetInboxTask: result.target_inbox_task,
      targetInboxTaskInfo: inboxTaskResult,
      targetInboxTaskTimeEventBlocks: inboxTaskResult?.time_event_blocks,
      targetBigPlan: result.target_big_plan,
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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id, activityId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.activity.timePlanActivityUpdate({
          ref_id: activityId,
          kind: {
            should_change: true,
            value: form.kind,
          },
          feasability: {
            should_change: true,
            value: form.feasability,
          },
        });

        return redirect(`/app/workspace/time-plans/${id}`);
      }

      case "archive": {
        await apiClient.activity.timePlanActivityArchive({
          ref_id: activityId,
        });

        return redirect(`/app/workspace/time-plans/${id}`);
      }

      case "remove": {
        await apiClient.activity.timePlanActivityRemove({
          ref_id: activityId,
        });

        return redirect(`/app/workspace/time-plans/${id}`);
      }

      case "target-inbox-task-mark-done":
      case "target-inbox-task-mark-not-done":
      case "target-inbox-task-start":
      case "target-inbox-task-restart":
      case "target-inbox-task-block":
      case "target-inbox-task-stop":
      case "target-inbox-task-reactivate":
      case "target-inbox-task-update": {
        const corePropertyEditable = isInboxTaskCoreFieldEditable(
          form.targetInboxTaskSource,
        );

        let status = form.targetInboxTaskStatus;
        if (form.intent === "target-inbox-task-mark-done") {
          status = InboxTaskStatus.DONE;
        } else if (form.intent === "target-inbox-task-mark-not-done") {
          status = InboxTaskStatus.NOT_DONE;
        } else if (form.intent === "target-inbox-task-start") {
          status = InboxTaskStatus.IN_PROGRESS;
        } else if (form.intent === "target-inbox-task-restart") {
          status = InboxTaskStatus.IN_PROGRESS;
        } else if (form.intent === "target-inbox-task-block") {
          status = InboxTaskStatus.BLOCKED;
        } else if (form.intent === "target-inbox-task-stop") {
          status = allowUserChanges(form.targetInboxTaskSource)
            ? InboxTaskStatus.NOT_STARTED
            : InboxTaskStatus.NOT_STARTED_GEN;
        } else if (form.intent === "target-inbox-task-reactivate") {
          status = allowUserChanges(form.targetInboxTaskSource)
            ? InboxTaskStatus.NOT_STARTED
            : InboxTaskStatus.NOT_STARTED_GEN;
        }

        const result = await apiClient.inboxTasks.inboxTaskUpdate({
          ref_id: form.targetInboxTaskRefId,
          name: corePropertyEditable
            ? {
                should_change: true,
                value: form.targetInboxTaskName,
              }
            : { should_change: false },
          status: {
            should_change: true,
            value: status,
          },
          project_ref_id: {
            should_change: true,
            value: form.targetInboxTaskProject,
          },
          big_plan_ref_id: {
            should_change: form.targetInboxTaskBigPlan !== undefined,
            value:
              form.targetInboxTaskBigPlan !== undefined &&
              form.targetInboxTaskBigPlan !== "none"
                ? form.targetInboxTaskBigPlan
                : undefined,
          },
          is_key: corePropertyEditable
            ? {
                should_change: true,
                value: form.targetInboxTaskIsKey,
              }
            : { should_change: false },
          eisen: corePropertyEditable
            ? {
                should_change: true,
                value: form.targetInboxTaskEisen,
              }
            : { should_change: false },
          difficulty: corePropertyEditable
            ? {
                should_change: true,
                value: form.targetInboxTaskDifficulty,
              }
            : { should_change: false },
          actionable_date: {
            should_change: true,
            value:
              form.targetInboxTaskActionableDate !== undefined &&
              form.targetInboxTaskActionableDate !== ""
                ? form.targetInboxTaskActionableDate
                : undefined,
          },
          due_date: {
            should_change: true,
            value:
              form.targetInboxTaskDueDate !== undefined &&
              form.targetInboxTaskDueDate !== ""
                ? form.targetInboxTaskDueDate
                : undefined,
          },
        });

        if (result.record_score_result) {
          return redirect(`/app/workspace/time-plans/${id}`, {
            headers: {
              "Set-Cookie": await saveScoreAction(result.record_score_result),
            },
          });
        }

        return redirect(`/app/workspace/time-plans/${id}`);
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

export default function TimePlanActivity() {
  const { id, activityId } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const timePlan = useRouteLoaderData<{ timePlan: TimePlan }>(
    "routes/app/workspace/time-plans/$id",
  )!.timePlan;
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const isBigScreen = useBigScreen();

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.timePlanActivity.archived;

  const inboxTaskTimeEventEntries = (
    loaderData.targetInboxTaskTimeEventBlocks || []
  ).map((block) => ({
    time_event_in_tz: timeEventInDayBlockToTimezone(
      block,
      topLevelInfo.user.timezone,
    ),
    entry: {
      inbox_task: loaderData.targetInboxTask!,
      time_events: [block],
    },
  }));
  const sortedInboxTaskTimeEventEntries = sortInboxTaskTimeEventsNaturally(
    inboxTaskTimeEventEntries,
  );

  let newInboxTaskTimeEventLocation = undefined;

  if (
    loaderData.targetInboxTask &&
    (timePlan.period === RecurringTaskPeriod.DAILY ||
      timePlan.period === RecurringTaskPeriod.WEEKLY)
  ) {
    const params = new URLSearchParams({
      date: timePlan.start_date,
      period: timePlan.period,
      view: "calendar",
      inboxTaskRefId: loaderData.targetInboxTask!.ref_id,
      timePlanReason: "for-time-plan",
      timePlanRefId: id as string,
      timePlanActivityRefId: activityId as string,
    });

    newInboxTaskTimeEventLocation = `/app/workspace/calendar/time-event/in-day-block/new-for-inbox-task?${params.toString()}`;
  }

  return (
    <LeafPanel
      fakeKey={`time-plan-${id}/activity-${activityId}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.timePlanActivity.archived}
      returnLocation={`/app/workspace/time-plans/${id}`}
      initialExpansionState={LeafPanelExpansionState.MEDIUM}
    >
      <GlobalError actionResult={actionData} />
      <SectionCard
        id="time-plan-activity-properties"
        title="Properties"
        actions={
          <SectionActions
            id="time-plan-activity-properties"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                text: "Save",
                value: "update",
                highlight: true,
              }),
            ]}
          />
        }
      >
        <Stack
          spacing={2}
          useFlexGap
          direction={isBigScreen ? "row" : "column"}
        >
          <FormControl fullWidth>
            <FormLabel id="kind">Kind</FormLabel>
            <TimePlanActivitKindSelect
              name="kind"
              defaultValue={loaderData.timePlanActivity.kind}
              inputsEnabled={inputsEnabled}
            />
            <FieldError actionResult={actionData} fieldName="/kind" />
          </FormControl>

          <FormControl fullWidth>
            <FormLabel id="feasability">Feasability</FormLabel>
            <TimePlanActivityFeasabilitySelect
              name="feasability"
              defaultValue={loaderData.timePlanActivity.feasability}
              inputsEnabled={inputsEnabled}
            />
            <FieldError actionResult={actionData} fieldName="/feasability" />
          </FormControl>
        </Stack>
      </SectionCard>

      {loaderData.targetInboxTask && (
        <>
          <InboxTaskPropertiesEditor
            title="Inbox Task"
            showLinkToInboxTask
            intentPrefix="target-inbox-task"
            namePrefix="targetInboxTask"
            topLevelInfo={topLevelInfo}
            rootProject={loaderData.rootProject}
            allProjects={loaderData.allProjects}
            allBigPlans={loaderData.allBigPlans}
            inputsEnabled={inputsEnabled && !loaderData.targetInboxTask.archived}
            inboxTask={loaderData.targetInboxTask} 
            inboxTaskInfo={loaderData.targetInboxTaskInfo!}
            actionData={actionData}
          />

          {isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.SCHEDULE,
          ) && (
            <TimeEventInDayBlockStack
              topLevelInfo={topLevelInfo}
              inputsEnabled={inputsEnabled}
              title="Time Events"
              createLocation={newInboxTaskTimeEventLocation}
              entries={sortedInboxTaskTimeEventEntries}
            />
          )}
        </>
      )}

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.BIG_PLANS,
      ) &&
        loaderData.targetBigPlan && (
          <SectionCard
            id="target"
            title="Big Plan"
            actions={
              <SectionActions
                id="target-big-plan"
                topLevelInfo={topLevelInfo}
                inputsEnabled={inputsEnabled}
                actions={[
                  NavMultipleSpread({
                    navs: [
                      NavSingle({
                        text: "New Inbox Task",
                        link: `/app/workspace/inbox-tasks/new?timePlanReason=for-time-plan&timePlanRefId=${id}&bigPlanReason=for-big-plan&bigPlanRefId=${loaderData.targetBigPlan.ref_id}&parentTimePlanActivityRefId=${activityId}`,
                        highlight: true,
                      }),
                      NavSingle({
                        text: "From Current Inbox Tasks",
                        link: `/app/workspace/time-plans/${id}/add-from-current-inbox-tasks?bigPlanReason=for-big-plan&bigPlanRefId=${loaderData.targetBigPlan.ref_id}&timePlanActivityRefId=${activityId}`,
                      }),
                    ],
                  }),
                ]}
              />
            }
          >
            <BigPlanStack
              topLevelInfo={topLevelInfo}
              showOptions={{
                showDonePct: true,
                showStatus: true,
                showProject: true,
                showEisen: true,
                showDifficulty: true,
                showActionableDate: true,
                showDueDate: true,
                showHandleMarkDone: false,
                showHandleMarkNotDone: false,
              }}
              bigPlans={[loaderData.targetBigPlan]}
            />
          </SectionCard>
        )}
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/time-plans",
  ParamsSchema,
  {
    notFound: (params) =>
      `Could not find activity ${params.activityId} in time plan ${params.id}!`,
    error: (params) =>
      `There was an error loading activity ${params.activityId} in time plan ${params.id}! Please try again!`,
  },
);

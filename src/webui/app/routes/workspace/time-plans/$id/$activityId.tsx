import type { InboxTask } from "@jupiter/webapi-client";
import {
  ApiError,
  InboxTaskStatus,
  TimePlanActivityFeasability,
  TimePlanActivityKind,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import {
  Button,
  FormControl,
  FormLabel,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  Link,
  useActionData,
  useFetcher,
  useParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { BigPlanStack } from "~/components/big-plan-stack";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { SectionCard } from "~/components/infra/section-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { timePlanActivityFeasabilityName } from "~/logic/domain/time-plan-activity-feasability";
import { timePlanActivityKindName } from "~/logic/domain/time-plan-activity-kind";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
  activityId: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
  kind: z.nativeEnum(TimePlanActivityKind),
  feasability: z.nativeEnum(TimePlanActivityFeasability),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { activityId } = parseParams(params, ParamsSchema);

  try {
    const result = await getLoggedInApiClient(
      session
    ).timePlans.timePlanActivityLoad({
      ref_id: activityId,
      allow_archived: true,
    });

    return json({
      timePlanActivity: result.time_plan_activity,
      targetInboxTask: result.target_inbox_task,
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

export async function action({ request, params }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id, activityId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await getLoggedInApiClient(session).timePlans.timePlanActivityUpdate({
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

        return redirect(`/workspace/time-plans/${id}/${activityId}`);
      }

      case "archive": {
        await getLoggedInApiClient(session).timePlans.timePlanActivityArchive({
          ref_id: activityId,
        });

        return redirect(`/workspace/time-plans/${id}/${activityId}`);
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
  const actionData = useActionData<typeof action>();
  const transition = useTransition();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    transition.state === "idle" && !loaderData.timePlanActivity.archived;

  const [kind, setKind] = useState(loaderData.timePlanActivity.kind);
  const [feasability, setFeasability] = useState(
    loaderData.timePlanActivity.feasability
  );

  useEffect(() => {
    setKind(loaderData.timePlanActivity.kind);
    setFeasability(loaderData.timePlanActivity.feasability);
  }, [loaderData]);

  const cardActionFetcher = useFetcher();

  function handleInboxTaskMarkDone(it: InboxTask) {
    cardActionFetcher.submit(
      {
        id: it.ref_id,
        status: InboxTaskStatus.DONE,
      },
      {
        method: "post",
        action: "/workspace/inbox-tasks/update-status-and-eisen",
      }
    );
  }

  function handleInboxTaskMarkNotDone(it: InboxTask) {
    cardActionFetcher.submit(
      {
        id: it.ref_id,
        status: InboxTaskStatus.NOT_DONE,
      },
      {
        method: "post",
        action: "/workspace/inbox-tasks/update-status-and-eisen",
      }
    );
  }

  return (
    <LeafPanel
      key={`time-plan-${id}/activity-${activityId}`}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation={`/workspace/time-plans/${id}`}
      initialExpansionState={LeafPanelExpansionState.MEDIUM}
    >
      <GlobalError actionResult={actionData} />
      <SectionCard
        title="Properties"
        actions={[
          <Button
            key="save"
            variant="contained"
            disabled={!inputsEnabled}
            type="submit"
            name="intent"
            value="update"
          >
            Save
          </Button>,
        ]}
      >
        <Stack spacing={2} useFlexGap>
          <FormControl fullWidth>
            <FormLabel id="kind">Kind</FormLabel>
            <ToggleButtonGroup
              value={kind}
              exclusive
              onChange={(_, newKind) => setKind(newKind)}
            >
              <ToggleButton
                disabled={!inputsEnabled}
                value={TimePlanActivityKind.FINISH}
              >
                {timePlanActivityKindName(TimePlanActivityKind.FINISH)}
              </ToggleButton>
              <ToggleButton
                disabled={!inputsEnabled}
                value={TimePlanActivityKind.MAKE_PROGRESS}
              >
                {timePlanActivityKindName(TimePlanActivityKind.MAKE_PROGRESS)}
              </ToggleButton>
            </ToggleButtonGroup>
            <input name="kind" type="hidden" value={kind} />
            <FieldError actionResult={actionData} fieldName="/kind" />
          </FormControl>

          <FormControl fullWidth>
            <FormLabel id="feasability">Feasability</FormLabel>
            <ToggleButtonGroup
              value={feasability}
              exclusive
              onChange={(_, newFeasability) => setFeasability(newFeasability)}
            >
              <ToggleButton
                disabled={!inputsEnabled}
                value={TimePlanActivityFeasability.MUST_DO}
              >
                {timePlanActivityFeasabilityName(
                  TimePlanActivityFeasability.MUST_DO
                )}
              </ToggleButton>
              <ToggleButton
                disabled={!inputsEnabled}
                value={TimePlanActivityFeasability.NICE_TO_HAVE}
              >
                {timePlanActivityFeasabilityName(
                  TimePlanActivityFeasability.NICE_TO_HAVE
                )}
              </ToggleButton>
              <ToggleButton
                disabled={!inputsEnabled}
                value={TimePlanActivityFeasability.STRETCH}
              >
                {timePlanActivityFeasabilityName(
                  TimePlanActivityFeasability.STRETCH
                )}
              </ToggleButton>
            </ToggleButtonGroup>
            <input name="feasability" type="hidden" value={feasability} />
            <FieldError actionResult={actionData} fieldName="/feasability" />
          </FormControl>
        </Stack>
      </SectionCard>

      {loaderData.targetInboxTask && (
        <SectionCard title="Target Inbox Task">
          <InboxTaskStack
            topLevelInfo={topLevelInfo}
            showOptions={{
              showStatus: true,
              showDueDate: true,
              showHandleMarkDone: true,
              showHandleMarkNotDone: true,
            }}
            inboxTasks={[loaderData.targetInboxTask]}
            onCardMarkDone={handleInboxTaskMarkDone}
            onCardMarkNotDone={handleInboxTaskMarkNotDone}
          />
        </SectionCard>
      )}

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.BIG_PLANS
      ) &&
        loaderData.targetBigPlan && (
          <SectionCard
            title="Target Big Plan"
            actions={[
              <Button
                key="new-inbox-task"
                variant="outlined"
                disabled={!inputsEnabled}
                to={`/workspace/inbox-tasks/new?timePlanReason=for-time-plan&timePlanRefId=${id}&bigPlanReason=for-big-plan&bigPlanRefId=${loaderData.targetBigPlan.ref_id}`}
                component={Link}
              >
                New Inbox Task
              </Button>,
              <Button
                key="from-current-inbox-tasks"
                variant="outlined"
                disabled={!inputsEnabled}
                to={`/workspace/time-plans/${id}/add-from-current-inbox-tasks?bigPlanReason=for-big-plan&bigPlanRefId=${loaderData.targetBigPlan.ref_id}`}
                component={Link}
              >
                From Current Inbox Tasks
              </Button>,
            ]}
          >
            <BigPlanStack
              topLevelInfo={topLevelInfo}
              showOptions={{
                showStatus: true,
                showParent: true,
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

export const CatchBoundary = makeCatchBoundary(
  () =>
    `Could not find time plan activity #${useParams().id}:#${
      useParams().activityId
    }!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading time plan activity #${useParams().id}:#${
      useParams().activityId
    }! Please try again!`
);

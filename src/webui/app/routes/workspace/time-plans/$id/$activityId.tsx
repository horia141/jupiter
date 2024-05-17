import { ApiError, BigPlan, BigPlanStatus, InboxTask, InboxTaskStatus, TimePlanActivityFeasability, TimePlanActivityKind, WorkspaceFeature } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  Stack,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useFetcher, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { BigPlanStack } from "~/components/big-plan-stack";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
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
      allow_archived: true
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
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    transition.state === "idle" && !loaderData.timePlanActivity.archived;

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

  function handleBigPlanMarkDone(bp: BigPlan) {
    cardActionFetcher.submit(
      {
        id: bp.ref_id,
        status: BigPlanStatus.DONE,
      },
      {
        method: "post",
        action: "/workspace/big-plans/update-status",
      }
    );
  }

  function handleBigPlanMarkNotDone(bp: BigPlan) {
    cardActionFetcher.submit(
      {
        id: bp.ref_id,
        status: BigPlanStatus.NOT_DONE,
      },
      {
        method: "post",
        action: "/workspace/big-plans/update-status",
      }
    );
  }

  return (
    <LeafPanel
      key={`time-plan-activity-${loaderData.timePlanActivity.ref_id}`}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation={`/workspace/time-plans/${id}`}
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="kind">Kind</InputLabel>
              <ButtonGroup>
                <Button
                  variant="contained"
                  disabled={!inputsEnabled}
                  name="kind"
                  value={TimePlanActivityKind.FINISH}
                >
                  Finish
                </Button>
                <Button
                  variant="contained"
                  disabled={!inputsEnabled}
                  name="kind"
                  value={TimePlanActivityKind.MAKE_PROGRESS}
                >
                  Make Progress
                </Button>
              </ButtonGroup>
              <FieldError actionResult={actionData} fieldName="/kind" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="feasability">Feasability</InputLabel>
              <ButtonGroup>
                <Button
                  variant="contained"
                  disabled={!inputsEnabled}
                  name="feasability"
                  value={TimePlanActivityFeasability.MUST_DO}
                >
                  Must Do
                </Button>
                <Button
                  variant="contained"
                  disabled={!inputsEnabled}
                  name="feasability"
                  value={TimePlanActivityFeasability.NICE_TO_HAVE}
                >
                  Nice To Have
                </Button>
                <Button
                  variant="contained"
                  disabled={!inputsEnabled}
                  name="feasability"
                  value={TimePlanActivityFeasability.STRETCH}
                >
                  Stretch
                </Button>
              </ButtonGroup>
              <FieldError actionResult={actionData} fieldName="/feasability" />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="update"
            >
              Save
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>

      {loaderData.targetInboxTask && (
        <InboxTaskStack
          topLevelInfo={topLevelInfo}
          showLabel
          showOptions={{
            showStatus: true,
            showDueDate: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Target Inbox Task"
          inboxTasks={[loaderData.targetInboxTask]}
          onCardMarkDone={handleInboxTaskMarkDone}
          onCardMarkNotDone={handleInboxTaskMarkNotDone}
        />
      )}

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.BIG_PLANS
      ) &&
        loaderData.targetBigPlan && (
          <BigPlanStack
            topLevelInfo={topLevelInfo}
            showLabel
            label="Target Big Plan"
            bigPlans={[loaderData.targetBigPlan]}
            onCardMarkDone={handleBigPlanMarkDone}
            onCardMarkNotDone={handleBigPlanMarkNotDone}
          />
        )}
    </LeafPanel>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () =>
    `Could not find time plan activity #${useParams().id}:#${
      useParams().itemId
    }!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading time plan activity #${useParams().id}:#${
      useParams().activityId
    }! Please try again!`
);

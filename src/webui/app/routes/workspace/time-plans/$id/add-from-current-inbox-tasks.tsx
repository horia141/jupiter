import { ApiError, TimePlanActivityTarget } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  Stack,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { InboxTaskCard } from "~/components/inbox-task-card";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import type { InboxTaskParent } from "~/logic/domain/inbox-task";
import {
  inboxTaskFindEntryToParent,
  sortInboxTasksByEisenAndDifficulty,
} from "~/logic/domain/inbox-task";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
  targetInboxTaskRefIds: z.string().transform((s) => s.split(",")),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);

  try {
    const timePlanResult = await getLoggedInApiClient(
      session
    ).timePlans.timePlanLoad({
      ref_id: id,
      allow_archived: false,
    });

    const inboxTasksResult = await getLoggedInApiClient(
      session
    ).inboxTasks.inboxTaskFind({
      allow_archived: false,
      include_notes: false,
      filter_just_workable: true,
    });

    return json({
      timePlan: timePlanResult.time_plan,
      activities: timePlanResult.activities,
      inboxTasks: inboxTasksResult.entries,
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
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "add": {
        await getLoggedInApiClient(
          session
        ).timePlans.timePlanAssociateWithInboxTasks({
          ref_id: id,
          inbox_task_ref_id: form.targetInboxTaskRefIds,
        });

        return redirect(`/workspace/time-plans/${id}`);
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

export default function TimePlanAddFromCurrentInboxTasks() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    transition.state === "idle" && !loaderData.timePlan.archived;

  const [targetInboxTasksRefIds, setTargetInboxTasksRefIds] = useState<
    Set<string>
  >(
    new Set(
      loaderData.activities
        .filter((tpa) => tpa.target === TimePlanActivityTarget.INBOX_TASK)
        .map((tpa) => tpa.ref_id)
    )
  );

  const sortedInboxTasks = sortInboxTasksByEisenAndDifficulty(
    loaderData.inboxTasks.map(e => e.inbox_task)
  );

  const entriesByRefId: { [key: string]: InboxTaskParent } = {};
  for (const entry of loaderData.inboxTasks) {
    entriesByRefId[entry.inbox_task.ref_id] = inboxTaskFindEntryToParent(entry);
  }

  return (
    <LeafPanel
      key={`time-plan-${id}/add-from-current-inbox-tasks`}
      returnLocation={`/workspace/time-plans/${id}`}
      initialExpansionState={LeafPanelExpansionState.LARGE}
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            {sortedInboxTasks.map((inboxTask) => (
              <InboxTaskCard
                key={`inbox-task-${inboxTask.ref_id}`}
                topLevelInfo={topLevelInfo}
                inboxTask={inboxTask}
                compact
                allowSelect
                selected={targetInboxTasksRefIds.has(inboxTask.ref_id)}
                showOptions={{
                  showProject: true,
                  showEisen: true,
                  showDifficulty: true,
                  showDueDate: true,
                  showParent: true,
                }}
                parent={entriesByRefId[inboxTask.ref_id]}
                onClick={(it) =>
                  setTargetInboxTasksRefIds((itri) =>
                    toggleInboxTaskRefIds(itri, it.ref_id)
                  )
                }
              />
            ))}
          </Stack>
        </CardContent>

        <input
          name="targetInboxTasksRefIds"
          type="hidden"
          value={new Array(targetInboxTasksRefIds).join(",")}
        />

        <CardActions>
          <ButtonGroup>
            <Button
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="add"
            >
              Add
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafPanel>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find time plan  #${useParams().id}`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading time plan activity #${
      useParams().id
    }. Please try again!`
);

function toggleInboxTaskRefIds(
  inboxTaskRefIds: Set<string>,
  newRefId: string
): Set<string> {
  if (inboxTaskRefIds.has(newRefId)) {
    const newInboxTaskRefIds = new Set<string>();
    for (const ri of inboxTaskRefIds.values()) {
      if (ri === newRefId) {
        continue;
      }
      newInboxTaskRefIds.add(ri);
    }
    return newInboxTaskRefIds;
  } else {
    const newInboxTaskRefIds = new Set<string>();
    for (const ri of inboxTaskRefIds.values()) {
      newInboxTaskRefIds.add(ri);
    }
    newInboxTaskRefIds.add(newRefId);
    return newInboxTaskRefIds;
  }
}

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
import { BigPlanCard } from "~/components/big-plan-card";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import type { BigPlanParent } from "~/logic/domain/big-plan";
import {
  bigPlanFindEntryToParent,
  sortBigPlansNaturally,
} from "~/logic/domain/big-plan";
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
  targetBigPlanRefIds: z.string().transform((s) => s.split(",")),
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

    const bigPlansResult = await getLoggedInApiClient(
      session
    ).bigPlans.bigPlanFind({
      allow_archived: false,
      include_notes: false,
      filter_just_workable: true,
      include_project: true,
      include_inbox_tasks: false,
    });

    return json({
      timePlan: timePlanResult.time_plan,
      activities: timePlanResult.activities,
      bigPlans: bigPlansResult.entries,
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
        ).timePlans.timePlanAssociateWithBigPlans({
          ref_id: id,
          big_plan_ref_ids: form.targetBigPlanRefIds,
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

export default function TimePlanAddFromCurrentBigPlans() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    transition.state === "idle" && !loaderData.timePlan.archived;

  const alreadyIncludedBigPlanRefIds = new Set(
    loaderData.activities
      .filter((tpa) => tpa.target === TimePlanActivityTarget.BIG_PLAN)
      .map((tpa) => tpa.target_ref_id)
  );

  const [targetBigPlanRefIds, setTargetBigPlanRefIds] = useState(
    new Set<string>()
  );

  const sortedBigPlans = sortBigPlansNaturally(
    loaderData.bigPlans.map((e) => e.big_plan)
  );

  const entriesByRefId: { [key: string]: BigPlanParent } = {};
  for (const entry of loaderData.bigPlans) {
    entriesByRefId[entry.big_plan.ref_id] = bigPlanFindEntryToParent(entry);
  }

  return (
    <LeafPanel
      key={`time-plan-${id}/add-from-current-big-plans`}
      returnLocation={`/workspace/time-plans/${id}`}
      initialExpansionState={LeafPanelExpansionState.LARGE}
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            {sortedBigPlans.map((bigPlan) => (
              <BigPlanCard
                key={`big-plan-${bigPlan.ref_id}`}
                topLevelInfo={topLevelInfo}
                bigPlan={bigPlan}
                compact
                allowSelect
                selected={
                  alreadyIncludedBigPlanRefIds.has(bigPlan.ref_id) ||
                  targetBigPlanRefIds.has(bigPlan.ref_id)
                }
                showOptions={{
                  showDueDate: true,
                  showParent: true,
                }}
                parent={entriesByRefId[bigPlan.ref_id]}
                onClick={(it) => {
                  if (alreadyIncludedBigPlanRefIds.has(bigPlan.ref_id)) {
                    return;
                  }

                  setTargetBigPlanRefIds((itri) =>
                    toggleBigPlanRefIds(itri, it.ref_id)
                  );
                }}
              />
            ))}
          </Stack>
        </CardContent>

        <input
          name="targetBigPlanRefIds"
          type="hidden"
          value={Array.from(targetBigPlanRefIds).join(",")}
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

function toggleBigPlanRefIds(
  bigPlanRefIds: Set<string>,
  newRefId: string
): Set<string> {
  if (bigPlanRefIds.has(newRefId)) {
    const newBigPlanRefIds = new Set<string>();
    for (const ri of bigPlanRefIds.values()) {
      if (ri === newRefId) {
        continue;
      }
      newBigPlanRefIds.add(ri);
    }
    return newBigPlanRefIds;
  } else {
    const newBigPlanRefIds = new Set<string>();
    for (const ri of bigPlanRefIds.values()) {
      newBigPlanRefIds.add(ri);
    }
    newBigPlanRefIds.add(newRefId);
    return newBigPlanRefIds;
  }
}

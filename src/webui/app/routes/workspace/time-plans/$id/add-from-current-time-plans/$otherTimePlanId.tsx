import { ApiError, RecurringTaskPeriod } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
} from "@mui/material";
import { ActionArgs, LoaderArgs, json, redirect } from "@remix-run/node";
import { ShouldRevalidateFunction, useActionData, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { TimePlanActivityCard } from "~/components/time-plan-activity-card";
import { TimePlanCard } from "~/components/time-plan-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { oneMoreThanPeriod } from "~/logic/domain/period";
import { sortTimePlanActivitiesNaturally } from "~/logic/domain/time-plan-activity";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
  otherTimePlanId: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
  targetActivitiesRefIds: z.string().transform((s) => s.split(",")),
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id, otherTimePlanId } = parseParams(params, ParamsSchema);

  try {
    const mainResult = await getLoggedInApiClient(
      session
    ).timePlans.timePlanLoad({
      ref_id: id,
      allow_archived: false,
    });

    const otherResult = await getLoggedInApiClient(
      session
    ).timePlans.timePlanLoad({
      ref_id: otherTimePlanId,
      allow_archived: true,
    });

    let higherTimePlan = undefined;
    if (otherResult.time_plan.period !== RecurringTaskPeriod.YEARLY) {
      const higherPeriod = oneMoreThanPeriod(otherResult.time_plan.period);
      for (const otherSubTimePlan of otherResult.sub_period_time_plans) {
        if (otherSubTimePlan.period === higherPeriod) {
          higherTimePlan = otherSubTimePlan;
          break;
        }
      }
    }

    return json({
      mainTimePlan: mainResult.time_plan,
      mainActivities: mainResult.activities,
      otherTimePlan: otherResult.time_plan,
      otherActivities: otherResult.activities,
      previousTimePlan: otherResult.previous_time_plan,
      higherTimePlan: higherTimePlan,
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
  const { id, otherTimePlanId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "add": {
        await getLoggedInApiClient(
          session
        ).timePlans.timePlanAssociateWithActivities({
          ref_id: id,
          other_time_plan_ref_id: otherTimePlanId,
          activity_ref_ids: form.targetActivitiesRefIds,
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

export default function TimePlanAddFromCurrentTimePlans() {
  const { id, otherTimePlanId } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    transition.state === "idle" && !loaderData.mainTimePlan.archived;

  const [targetActivitiesRefIds, setTargetActivitiesRefIds] = useState<
    Set<string>
  >(
    new Set(
      loaderData.otherActivities
        .filter(
          (s) =>
            loaderData.mainActivities.findIndex(
              (r) =>
                r.target === s.target && r.target_ref_id === s.target_ref_id
            ) !== -1
        )
        .map((tpa) => tpa.ref_id)
    )
  );

  const sortedOtherActivities = sortTimePlanActivitiesNaturally(
    loaderData.otherActivities
  );

  return (
    <LeafPanel
      key={`time-plan-${id}:add-from-current-time-plans:${otherTimePlanId}`}
      returnLocation={`/workspace/time-plans/${id}`}
      initialExpansionState={LeafPanelExpansionState.LARGE}
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          {sortedOtherActivities.map((activity) => (
            <TimePlanActivityCard
              key={`time-plan-activity-${activity.ref_id}`}
              topLevelInfo={topLevelInfo}
              timePlan={loaderData.otherTimePlan}
              activity={activity}
              allowSelect
              selected={targetActivitiesRefIds.has(activity.ref_id)}
              onClick={(a) =>
                setTargetActivitiesRefIds((at) =>
                  toggleActivitiesRefIds(at, activity.ref_id)
                )
              }
            />
          ))}
        </CardContent>

        {loaderData.previousTimePlan && (
          <TimePlanCard
            topLevelInfo={topLevelInfo}
            timePlan={loaderData.previousTimePlan}
          />
        )}

        {loaderData.higherTimePlan && (
          <TimePlanCard
            topLevelInfo={topLevelInfo}
            timePlan={loaderData.higherTimePlan}
          />
        )}

        <input
          name="targetActivitiesRefIds"
          type="hidden"
          value={new Array(targetActivitiesRefIds).join(",")}
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
  () =>
    `Could not find time plan  #${useParams().id}:#${
      useParams().otherTimePlanId
    }`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading time plan activity #${useParams().id}:#${
      useParams().otherTimePlanId
    }. Please try again!`
);

function toggleActivitiesRefIds(
  ActivitiesRefIds: Set<string>,
  newRefId: string
): Set<string> {
  if (ActivitiesRefIds.has(newRefId)) {
    const newActivitiesRefIds = new Set<string>();
    for (const ri of ActivitiesRefIds.values()) {
      if (ri === newRefId) {
        continue;
      }
      newActivitiesRefIds.add(ri);
    }
    return newActivitiesRefIds;
  } else {
    const newActivitiesRefIds = new Set<string>();
    for (const ri of ActivitiesRefIds.values()) {
      newActivitiesRefIds.add(ri);
    }
    newActivitiesRefIds.add(newRefId);
    return newActivitiesRefIds;
  }
}
